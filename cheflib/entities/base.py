#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: cheflib.py
#
# Copyright 2024 Daan de Goede, Costas Tyfoxylos
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""
Chef base entity.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""
from collections.abc import Generator
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional
import math
import concurrent.futures

from chefsessionlib import ChefSession
from cheflib.cheflibexceptions import InvalidObject

ENTITY_URI = {
    'client': 'clients',
    'cookbook': 'cookbooks',
    'databag': 'data',
    'environment': 'environments',
    'node': 'nodes',
    'role': 'roles'
}
MAX_ROWS = 1000


@dataclass
class Entity:
    _session: ChefSession
    _name: str
    _url: str
    _data: Optional[Dict] = None

    def _save_data(self, data: dict):
        payload = deepcopy(self.data)
        payload.update(data)
        response = self._session.put(self._url, json=payload)
        if not response.ok:
            raise InvalidObject
        self._data = response.json()

    @property
    def data(self):
        if self._data is None:
            response = self._session.get(self._url)
            if not response.ok:
                raise InvalidObject
            self._data = response.json()
        return self._data

    @property
    def name(self):
        return self.data.get('name')

    def update_data(self):
        """"""

    def delete(self) -> bool:
        """Delete entity"""
        response = self._session.delete(self._url)  # noqa
        if not response.ok:
            # log DeleteFailed(f"Failed to delete '{co.name}, reason:\n{response.text}")
            pass
        return response.ok


class EntityManager:
    """Manages entities by making them act like iterables but also implements contains and other useful stuff."""

    # pylint: disable=too-many-arguments
    def __init__(self, session, entity_object, url, primary_match_field='name'):
        self._session = session
        self._max_http_workers = 4
        self._object_type = entity_object
        self._primary_match_field = primary_match_field
        self._next_state = None
        self._entities_keys = None
        self._url = url

    @property
    def _objects(self):
        return self._get_entity_objects()

    def _get_paginated_response(self, url, params=None, keys=None) -> Generator:
        method = getattr(self._session, 'get')
        if keys is not None:
            method = getattr(self._session, 'post')
        else:
            keys = {}
        if not params:
            params = {}
        response = method(url, params=params, json=keys)
        if not response.ok:
            # log shizzle
            return False
        response_data = response.json()
        total = response_data.get('total', 0)
        rows = params.get('rows', MAX_ROWS)
        # self._logger.debug('Calculated that there are %s pages to get', page_count)
        yield from response_data.get('rows', response_data.items())
        if total > rows:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_http_workers) as executor:
                futures = []
                for start in range(rows, total, rows):
                    params.update({'start': start})
                    futures.append(executor.submit(method, url, params=params.copy(), json=keys.copy()))
                for future in concurrent.futures.as_completed(futures):
                    try:
                        response = future.result()
                        response_data = response.json()
                        response.close()
                        yield from response_data.get('rows')
                    except Exception:  # pylint: disable=broad-except
                        # self._logger.exception('Future failed...')
                        pass

    def _get_entity_objects(self, query: str = None, keys: dict = None, rows: int = MAX_ROWS) -> Generator:
        """Get the entity objects from the chef server

        If a query is provided it will use the search API otherwise it will use the default entity API

        Args:
            query: String containing the search query
            keys: Dictionary with the fields to include in the results

        Returns:
            Generator that yields entity objects

        """
        module = __import__('cheflib.entities')
        entity_object = getattr(module, self._object_type)
        if not entity_object:
            # log Could not find 'entity'!
            return None
        url = self._url
        params = None
        if query is not None:
            params = {'q': query,
                      'rows': rows,
                      'start': 0}
        entities = self._get_paginated_response(url, params=params, keys=keys)
        if query is not None:
            yield from (entity_object(self._session, entity['data']['name'], entity['url'])
                        for entity in entities)
        else:
            yield from (entity_object(self._session, key, value)
                        for key, value in entities)

    def __iter__(self):
        return self._objects

    def __contains__(self, value):
        return next(self.filter(f'{self._primary_match_field}:{value}'), False)

    def filter(self, query: str, keys: dict = None) -> Generator:
        """Implements filtering based on the filtering capabilities of chef.

        Args:
            keys: Dictionary of keys to response filter by.
            query: search query.

        Returns:
              Generator of the objects retrieved based on the filtering.

        """
        if keys is None:
            keys = {'name': ['name']}

        return self._get_entity_objects(query, keys, 20)
