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

from chefsessionlib import ChefSession
from cheflib.entities import (ENTITY_URI,
                              Entity,
                              EntityManager,
                              Client,
                              Cookbook,
                              DataBag,
                              Environment,
                              Node,
                              Role)

from .cheflibexceptions import (NodeNotFound,
                                InvalidSearchIndex,
                                CreateFailed,
                                DeleteFailed)

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
LOGGER_BASENAME = '''cheflib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

MAX_ROW_COUNT = 1000


class Chef:
    """Client to the Chef API.

    Uses ChefSessionLib to authenticate all calls to the chef server.

    """

    def __init__(self,
                 endpoint: str,
                 organization: str,
                 user_id: str,
                 private_key_contents: str,
                 client_version: str = '12.0.2',
                 authentication_version: str = '1.3',
                 api_version: int = 1):
        self.base_url = endpoint
        self.organization = organization
        self._search_indexes = None
        self._max_http_workers = 4
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
        session = ChefSession(user_id,
                              private_key_contents,
                              client_version,
                              authentication_version,
                              api_version)
        # The next call has dual functionality, we test authentication and retrieve the allowed search indexes
        response = session.get(f'{self._organization_url}/search')
        self._search_indexes = response.json()
        return session

    def _get_paginated_response(self, entity_object, query=None, keys=None, max_row_count: int = MAX_ROW_COUNT) -> Generator:
        http_method = getattr(self.session, 'post' if keys else 'get')
        keys = keys or {}
        params = {'q': query, 'rows': max_row_count, 'start': 0} if query else {}
        url = self._request_url(entity_object.__name__, params)
        response = http_method(url, params=params, json=keys)
        if not response.ok:
            # log shizzle
            return False
        response_data = response.json()
        total = response_data.get('total', 0)
        row_count = params.get('rows', MAX_ROW_COUNT)
        # self._logger.debug('Calculated that there are %s pages to get', page_count)
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
                    except Exception:  # pylint: disable=broad-except
                        # self._logger.exception('Future failed...')
                        pass

    def _create(self, url: str, data: dict) -> dict:
        """Create entity"""
        response = self.session.post(url, json=data)
        if not response.ok:
            raise CreateFailed(f"Failed to create '{data['name']}, reason:\n{response.text}")
        return response.json()

    def _request_url(self, entity: str, params: dict = None) -> str:
        """Returns the full organization url"""
        return f'{self._organization_url}/search/{entity.lower()}' if params else f'{self._organization_url}/{ENTITY_URI[entity.lower()]}'

    @property
    def _organization_url(self) -> str:
        """Returns the full organization url"""
        return f'{self.base_url}/organizations/{self.organization}'

    @property
    def clients(self) -> EntityManager:
        """List clients

        Returns:
            Generator for clients

        """
        return EntityManager(self, 'Client', self._organization_url)

    def create_client(self, name: str, data: dict = None) -> Client:
        """Create client"""
        data = data or {}
        data.update({'name': name})
        resp = self._create(f'{self._organization_url}/clients', data)
        return Client(self.session, name, resp['uri'], resp['chef_key'])

    def delete_client_by_name(self, name: str) -> bool:
        """Delete client
        """
        client = self.get_client_by_name(name)
        return client.delete()

    def search_clients(self, query: str = '*:*', keys: dict = None):
        """Search clients

        Args:
            query: Chef search query
            keys: dict with attribute names to return in the results

            keys example:
                {
                    'name': [ 'name' ],
                    'ip': [ 'ipaddress' ],
                    'kernel_version': [ 'kernel', 'version' ]
                }

        Returns:
            a list of Clients.
        """
        return EntityManager(self, 'Client', self._organization_url, 'name').filter(query, keys)

    def get_client_by_name(self, name: str) -> Client:
        """Find Client by name

        Args:
            name:

        Returns:
            Client: Client object

        """
        return next((client for client in self.clients if client.name.lower() == name.lower()), None)

    @property
    def cookbooks(self) -> EntityManager:
        """This represents knife cookbook list

        Returns:
            All cookbooks

        """
        return EntityManager(self, 'Cookbook', self._organization_url, 'name')

    @property
    def data_bags(self) -> EntityManager:
        """List data bagss

        Returns:
            Generator for data bags

        """
        return EntityManager(self, 'DataBag', self._organization_url, 'name')

    @property
    def environments(self) -> EntityManager:
        """List environments

        Returns:
            Generator for environments

        """
        return EntityManager(self, 'Environment', self._organization_url, 'name')

    @property
    def nodes(self) -> EntityManager:
        """List nodes

        Returns:
            Generator for nodes

        """
        return EntityManager(self, 'Node', self._organization_url, 'name')

    def create_node(self, name: str, data: dict = None) -> Node:
        """Create node"""
        data = data or {}
        data.update({'name': name})
        resp = self._create(f'{self._organization_url}/nodes', data)
        return Node(self.session, name, resp['uri'])

    def delete_node_by_name(self, name: str) -> bool:
        """Delete node
        """
        node = self.get_node_by_name(name)
        return node.delete()

    def search_nodes(self, query: str = '*:*', keys: dict = None):
        """Search nodes

        Args:
            query: Chef search query
            keys: dict with attribute names to return in the results

            keys example:
                {
                    'name': [ 'name' ],
                    'ip': [ 'ipaddress' ],
                    'kernel_version': [ 'kernel', 'version' ]
                }

        Returns:
            a list of Nodes.
        """
        return EntityManager(self, 'Node', self._organization_url, 'name').filter(query, keys)

    def get_node_by_name(self, name: str) -> Node:
        """Find Node by name

        Args:
            name:

        Returns:
            Node: Node object

        """
        return next((node for node in self.nodes if node.name.lower() == name.lower()), None)

    def get_node_by_ip_address(self, ipaddress) -> Node:
        """
        Use search get node by IP address

        Args:
            ipaddress

        Returns:
            Node: Node object

        """
        return next(EntityManager(self, 'Node', self._organization_url, 'name').filter(f'ipaddress:{ipaddress}'))

    @property
    def roles(self) -> EntityManager:
        """List roles

        Returns:
            Generator for roles

        """
        return EntityManager(self, 'Role', self._organization_url, 'name')

    def raw(self, uri, method='get', **kwargs):
        """Get raw data
        """
        url = f'{self._organization_url}/{uri}'
        response = getattr(self.session, method.lower())(url, **kwargs)
        return response
