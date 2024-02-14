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

from chefsessionlib import ChefSession
from cheflib.entities import (Entity,
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

    def _create(self, url: str, data: dict) -> dict:
        """Create entity"""
        response = self.session.post(url, json=data)
        if not response.ok:
            raise CreateFailed(f"Failed to create '{data['name']}, reason:\n{response.text}")
        return response.json()

    @property
    def _organization_url(self) -> str:
        """Returns the full organization url"""
        return f'{self.base_url}/organizations/{self.organization}'

    def _search(self, index, query, keys: dict = None):
        """Search chef"""

        """
        Response from server contains:
        total, start and rows (containing the data per found object)
        """
        rows = 1000
        start = 0
        if index not in self._search_indexes:
            raise InvalidSearchIndex(f"'{index}' is not a valid search index!")
        url = f'{self._organization_url}/search/{index}'
        params = {'q': query,
                  'rows': rows,
                  'start': start}
        if keys:
            response = self.session.post(url, params=params, json=keys)
            return response.json()
        response = self.session.get(url, params=params)
        return response.json()

    @property
    def clients(self) -> Generator:
        """List clients

        Returns:
            Generator for clients

        """
        url = f'{self._organization_url}/clients'
        yield from EntityManager(self.session, 'Client', url, 'name')

    @property
    def cookbooks(self) -> Generator:
        """This represents knife cookbook list

        Returns:
            All cookbooks

        """
        url = f'{self._organization_url}/cookbooks'
        yield from EntityManager(self.session, 'Cookbook', url, 'name')

    @property
    def data_bags(self) -> Generator:
        """List data bagss

        Returns:
            Generator for data bags

        """
        url = f'{self._organization_url}/data'
        yield from EntityManager(self.session, 'DataBag', url, 'name')

    @property
    def environments(self) -> Generator:
        """List environments

        Returns:
            Generator for environments

        """
        url = f'{self._organization_url}/environments'
        yield from EntityManager(self.session, 'Environment', url, 'name')

    @property
    def nodes(self) -> Generator:
        """List nodes

        Returns:
            Generator for nodes

        """
        url = f'{self._organization_url}/nodes'
        yield from EntityManager(self.session, 'Node', url, 'name')

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
        url = f'{self._organization_url}/search/node'
        yield from EntityManager(self.session, 'Node', url, 'name').filter(query, keys)

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
        node = self._search('node', f'ipaddress:{ipaddress}')
        return node

    @property
    def roles(self) -> Generator:
        """List roles

        Returns:
            Generator for roles

        """
        url = f'{self._organization_url}/roles'
        yield from EntityManager(self.session, 'Role', url, 'name')

    def raw(self, entity_type, method='get', **kwargs):
        """Get raw data
        """
        url = f'{self._organization_url}/{entity_type}'
        response = getattr(self.session, method.lower())(url, **kwargs)
        return response
