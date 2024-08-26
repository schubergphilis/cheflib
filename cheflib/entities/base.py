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
import logging
from collections.abc import Generator
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional

from cheflib.cheflibexceptions import InvalidObject
from cheflib.configuration import (ENTITY_URL,
                                   MAX_ROW_COUNT)

# This is the main prefix used for logging
LOGGER_BASENAME = 'base'
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


@dataclass
class Entity:
    _chef: 'Chef'  # noqa
    _name: str
    _url: str
    _data: Optional[Dict] = None

    def __post_init__(self):
        """"""
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')

    @classmethod
    def from_data(cls, chef_instance, data: Dict):
        """"""
        # the data could contain the URL to the object or the name of the object, the API is behaving one way
        # for certain get calls and another way for other calls.
        # If the URL is contained in the data dict, and the 'name' of the object can be extracted,
        # or the name of the object is part of the data dict, and we need to contruct the URL manually.
        url = data.get('url')
        if url:
            name = url.split('/')[-1]
        else:
            name = data.get('name')
            url = Entity._generate_entity_url(cls.__name__, chef_instance._organization_url , name)  # noqa
        return cls(chef_instance.session, name, url, data)

    @staticmethod
    def _generate_entity_url(class_name, organization_url: str, name: str, parent_name: str = None) -> str:
        """"""
        return f"{ENTITY_URL[class_name.lower()].format(organization_url=organization_url, parent_name=parent_name)}/{name}"

    def _pre_save_data(self, data: Dict) -> Dict:
        """"""
        return data

    def _save_data(self, data: dict):
        payload = deepcopy(self.data)
        payload.update(data)
        payload = self._pre_save_data(payload)
        response = self._chef.session.put(self._url, json=payload)
        if not response.ok:
            self._logger.debug(f'Unable to save data, Class: {hasattr(self, "__name__")}, url: {self._url}, '
                               f'data: {data}, payload: {payload}')
            raise InvalidObject(response.text)
        self._data = None

    @staticmethod
    def _post_data(self):
        """"""
        pass

    @property
    def data(self):
        if self._data is None:
            response = self._chef.session.get(self._url)
            if not response.ok:
                self._logger.debug(f'Unable to retrieve data, Class: {hasattr(self, "__name__")}, url: {self._url}')
                raise InvalidObject
            self._data = response.json()
        self._post_data(self)
        return self._data

    @data.setter
    def data(self, data: dict):
        """"""
        if not isinstance(data, dict):
            self._logger.debug(f'"data" is not a dict, but Class: {hasattr(data, "__name__")}')
            raise InvalidObject
        self._data = deepcopy(data)
        self._data.update(id=self.name)
        self._save_data(self._data)

    @property
    def name(self):
        return self._name

    def delete(self) -> bool:
        """Delete entity"""
        response = self._chef.session.delete(self._url)
        if not response.ok:
            self._logger.debug(f"Failed to delete '{self._url}, reason:\n{response.text}")
            pass
        return response.ok


class EntityManager:
    """Manages entities by making them act like iterables but also implements contains and other useful stuff."""

    # pylint: disable=too-many-arguments
    def __init__(self, chef_instance, entity_object, parent_name=None, primary_match_field='name'):
        self._chef = chef_instance
        self._object_type = entity_object
        self._next_state = None
        self._parent_name = parent_name
        self._primary_match_field = primary_match_field

    @property
    def _objects(self):
        return self._get_entity_objects()

    @staticmethod
    def _verify_entity_url(url) -> str:
        """"""
        if isinstance(url, dict) and 'url' in url:
            return url['url']
        return url

    def _get_entity_objects(self, query: str = None, keys: dict = None, max_row_count: int = MAX_ROW_COUNT) -> Generator:
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
        entities = self._chef._get_paginated_response(entity_object, query=query, keys=keys, max_row_count=max_row_count, parent_name=self._parent_name) # noqa
        # As mentioned in the documentation, when a 'query' was supplied, we get the responses from the search api,
        # which returns the data in a different format. If no query was supplied we simply use the getter of the entity.
        # This means we yield from a different generator.
        if query is not None:
            result = (entity_object.from_data(self._chef, entity.get('data', entity))
                      for entity in entities)
        else:
            result = (entity_object(self._chef, key, self._verify_entity_url(value))
                      for key, value in entities)
        yield from result

    def __iter__(self):
        return self._objects

    def __contains__(self, value):
        return next(self.filter(query=f'{self._primary_match_field}:{value}', keys={'name': ['name']}), False)

    def filter(self, query: str, keys: dict = None) -> Generator:
        """Implements filtering based on the filtering capabilities of chef.

        Args:
            keys: Dictionary of keys to response filter by.
            query: search query.

        Returns:
              Generator of the objects retrieved based on the filtering.

        """
        return self._get_entity_objects(query)
