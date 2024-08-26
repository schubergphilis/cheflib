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
Main code for cheflib.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

import logging
from collections.abc import Generator
import concurrent.futures
from typing import Optional

from chefsessionlib import ChefSession
from cheflib.entities import (Entity,
                              EntityManager,
                              Client,
                              ClientKey,
                              Cookbook,
                              DataBag,
                              Environment,
                              Node,
                              Role)

from .cheflibexceptions import (NodeNotFound,
                                InvalidSearchIndex,
                                CreateFailed,
                                DeleteFailed)
from .configuration import (ENTITY_URL,
                            MAX_ROW_COUNT)

__author__ = 'Daan de Goede <ddegoede@schubergphilis.com>, Costas Tyfoxylos <ctyfoxylos@schubergphilis.com>'
__docformat__ = 'google'
__date__ = '18-01-2024'
__copyright__ = 'Copyright 2024, Daan de Goede, Costas Tyfoxylos'
__credits__ = ["Daan de Goede", "Costas Tyfoxylos"]
__license__ = 'Apache Software License 2.0'
__maintainer__ = 'Daan de Goede, Costas Tyfoxylos'
__email__ = '<ddegoede@schubergphilis.com>, <ctyfoxylos@schubergphilis.com>'
__status__ = 'Development'  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = 'cheflib'
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class Chef:
    """"""

    def __init__(self,
                 endpoint: str,
                 organization: str,
                 user_id: str,
                 private_key_contents: str,
                 client_version: str = '12.0.2',
                 authentication_version: str = '1.3',
                 api_version: int = 1):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.base_url = endpoint
        self.organization = organization
        self._search_indexes = None
        self._max_http_workers = 4
        self._logger.debug(f'Initializing cheflib with following settings:\n'
                           f'organization: "{self.organization}"\n'
                           f'base_url: "{self.base_url}"\n'
                           f'max_http_workers: {self._max_http_workers}')
        self.session = self._get_authenticated_session(user_id,
                                                       private_key_contents,
                                                       client_version,
                                                       authentication_version,
                                                       api_version)

    def _get_authenticated_session(self,
                                   user_id,
                                   private_key_contents,
                                   client_version,
                                   authentication_version,
                                   api_version):
        """"""
        self._logger.debug(f'Instantiating ChefSession')
        session = ChefSession(user_id,
                              private_key_contents,
                              client_version,
                              authentication_version,
                              api_version)
        # The next call has dual functionality, we test authentication and retrieve the allowed search indexes
        self._logger.debug(f'Testing connectivity and gathering allowed search indexes')
        response = session.get(f'{self._organization_url}/search')
        self._search_indexes = response.json()
        return session

    def _get_paginated_response(self, entity_object, query=None, keys=None, parent_name: str = None, max_row_count: int = MAX_ROW_COUNT) -> Generator:
        """"""
        http_method = getattr(self.session, 'post' if keys else 'get')
        keys = keys or {}
        params = {'q': query, 'rows': max_row_count, 'start': 0} if query else {}
        url = self._request_url(entity_object.__name__, params, parent_name)
        response = http_method(url, params=params, json=keys)
        if not response.ok:
            self._logger.warning(f'Unable to retrieve paginated response for "{url}"')
            self._logger.debug(f'Parameters: {params}, keys: {keys}')
            return False
        response_data = response.json()
        total = response_data.get('total', 0)
        row_count = params.get('rows', MAX_ROW_COUNT)
        self._logger.debug(f'Calculated that there are {row_count} pages to retrieve')
        yield from response_data.get('rows', response_data.items())
        if total > row_count:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_http_workers) as executor:
                futures = []
                for start in range(row_count, total, row_count):
                    params.update({'start': start})
                    futures.append(executor.submit(http_method, url, params=params.copy(), json=keys.copy()))
                for future in concurrent.futures.as_completed(futures):
                    try:
                        response = future.result()
                        response_data = response.json()
                        response.close()
                        yield from response_data.get('rows')
                    except Exception as e:  # pylint: disable=broad-except
                        self._logger.exception(f'Future failed...\nreason: {e}')
                        pass

    def _create(self, url: str, data: dict) -> dict:
        """"""
        response = self.session.post(url, json=data)
        if not response.ok:
            raise CreateFailed(f"Failed to create '{data['name']}, reason:\n{response.text}")
        return response.json()

    def _request_url(self, entity: str, params: dict = None, parent_name=None) -> str:
        """"""
        if params:
            return f'{self._organization_url}/search/{entity.lower()}'
        return f'{ENTITY_URL[entity.lower()].format(organization_url=self._organization_url, parent_name=parent_name)}'

    @property
    def _organization_url(self) -> str:
        """"""
        return f'{self.base_url}/organizations/{self.organization}'

    @property
    def clients(self) -> EntityManager:
        """"""
        return EntityManager(self, 'Client', self._organization_url)

    def create_client(self, name: str, data: dict = None) -> Optional[Client]:
        """"""
        if data is None:
            data = {}
        if not name:
            # log shizzle
            return None
        data = data or {'create_key': True}
        data.update(name=name)
        resp = self._create(f'{self._organization_url}/clients', data)
        return Client(self, name, resp['uri'], resp['chef_key'])

    def delete_client_by_name(self, name: str) -> bool:
        """"""
        client = self.get_client_by_name(name)
        return client.delete()

    def search_clients(self, query: str = '*:*', keys: dict = None):
        """"""
        return EntityManager(self, 'Client', self._organization_url, 'name').filter(query, keys)

    def get_client_by_name(self, name: str) -> Client:
        """"""
        return next((client for client in self.clients if client.name.lower() == name.lower()), None)

    @property
    def cookbooks(self) -> EntityManager:
        """"""
        return EntityManager(self, 'Cookbook', self._organization_url, 'name')

    @property
    def data_bags(self) -> EntityManager:
        """"""
        return EntityManager(self, 'DataBag', self._organization_url, 'name')

    def create_data_bag(self, name: str) -> Optional[DataBag]:
        """"""
        if not name:
            # log shizzle
            return None
        data = {}
        data.update(name=name)
        resp = self._create(f'{self._organization_url}/data', data)
        return DataBag(self, name, resp['uri'])

    def get_data_bag_by_name(self, name: str) -> DataBag:
        """"""
        return next((data_bag for data_bag in self.data_bags if data_bag.name.lower() == name.lower()), None)

    def get_data_bag_item_by_name(self, bag_name: str, name: str, secret: bytes = None) -> DataBag:
        """"""
        db = self.get_data_bag_by_name(bag_name)
        return db.get_item_by_name(name, secret)

    @property
    def environments(self) -> EntityManager:
        """"""
        return EntityManager(self, 'Environment', self._organization_url, 'name')

    def create_environment(self, name: str, data: dict = None) -> Environment:
        """"""
        data = data or {}
        data.update(name=name)
        resp = self._create(f'{self._organization_url}/environments', data)
        return Environment(self, name, resp['uri'])

    def delete_environment_by_name(self, name: str) -> bool:
        """"""
        environment = self.get_environment_by_name(name)
        return environment.delete()

    def get_environment_by_name(self, name: str) -> Environment:
        """"""
        return next((environment for environment in self.environments if environment.name.lower() == name.lower()), None)

    @property
    def nodes(self) -> EntityManager:
        """"""
        return EntityManager(self, 'Node', self._organization_url, 'name')

    def create_node(self, name: str, data: dict = None) -> Node:
        """"""
        data = data or {}
        data.update({'name': name})
        resp = self._create(f'{self._organization_url}/nodes', data)
        return Node(self, name, resp['uri'])

    def delete_node_by_name(self, name: str) -> bool:
        """"""
        node = self.get_node_by_name(name)
        return node.delete()

    def search_nodes(self, query: str = '*:*', keys: dict = None):
        """"""
        return EntityManager(self, 'Node', self._organization_url, 'name').filter(query, keys)

    def get_node_by_name(self, name: str) -> Node:
        """"""
        return next((node for node in self.nodes if node.name.lower() == name.lower()), None)

    def get_node_by_ip_address(self, ipaddress) -> Node:
        """"""
        return next(EntityManager(self, 'Node', self._organization_url, 'name').filter(f'ipaddress:{ipaddress}'))

    @property
    def roles(self) -> EntityManager:
        """"""
        return EntityManager(self, 'Role', self._organization_url, 'name')

    def create_role(self, name: str, data: dict = None) -> Role:
        """"""
        data = data or {}
        data.update({'name': name})
        resp = self._create(f'{self._organization_url}/roles', data)
        return Role(self, name, resp['uri'])

    def delete_role_by_name(self, name: str) -> bool:
        """"""
        role = self.get_role_by_name(name)
        return role.delete()

    def get_role_by_name(self, name: str) -> Role:
        """"""
        return next((role for role in self.roles if role.name.lower() == name.lower()), None)

    def raw(self, uri, method='get', **kwargs):
        """"""
        url = f'{self._organization_url}/{uri}'
        self._logger.debug(f'Performing RAW api call, using method "{method.lower()}" to URL "{url}"')
        response = getattr(self, method.lower())(url, **kwargs)
        return response.json()
