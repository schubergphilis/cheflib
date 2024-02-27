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

from chefsessionlib import ChefSession
from cheflib.cheflibexceptions import InvalidObject

ENTITY_URI = {
    'client': 'clients',
    'client_key': 'clients',
    'cookbook': 'cookbooks',
    'cookbook_version': 'version',
    'databag': 'data',
    'environment': 'environments',
    'node': 'nodes',
    'role': 'roles'
}


def generate_entity_url(cls, organization_url: str, name: str) -> str:
    """"""
    return f'{organization_url}/{ENTITY_URI[cls.__name__.lower()]}/{name}'


@dataclass
class Entity:
    _session: ChefSession
    _name: str
    _url: str
    _data: Optional[Dict] = None

    @classmethod
    def from_data(cls, chef_instance, data: Dict):
        """"""
        name = data.get('name', '')
        url = data.get('url', generate_entity_url(cls, chef_instance._organization_url , name)) # noqa
        if not name:
            name = url.split('/')[-1]
        return cls(chef_instance.session, name, url, data)

    def _save_data(self, data: dict):
        payload = deepcopy(self.data)
        payload.update(data)
        response = self._session.put(self._url, json=payload)
        if not response.ok:
            # log something
            raise InvalidObject(response.text)
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
        return self._name

    def update_data(self):
        """"""

    def delete(self) -> bool:
        """Delete entity"""
        response = self._session.delete(self._url)
        if not response.ok:
            # log DeleteFailed(f"Failed to delete '{co.name}, reason:\n{response.text}")
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

    def _get_entity_objects(self, query: str = None, keys: dict = None) -> Generator:
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
        # TODO remove row_count before publication, just in place to force pagination.
        entities = self._chef._get_paginated_response(entity_object, query=query, keys=keys, max_row_count=20) # noqa
        if query is not None:
            result = (entity_object.from_data(self._chef, entity.get('data', entity))
                      for entity in entities)
        else:
            result = (entity_object(self._chef.session, key, value)
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
        return self._get_entity_objects(query, keys)
