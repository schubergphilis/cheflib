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
from chefsessionlib import ChefSession
from cheflib.entities.base import Node
from .cheflibexceptions import (InvalidAuthentication,
                         NodeNotFound,
                         InvalidSearchIndex)

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

    Most calls will require authorization. Use the authenticate()
    method to authorize this client's session.
    """

    def __init__(self,
                 endpoint,
                 organization,
                 user_id,
                 private_key_contents,
                 client_version='12.0.2',
                 authentication_version='1.0',
                 api_version=1):
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
        # We need to check how the remote actually responds on error. Check wrong username, wrong pem, garbage on pem
        # and so on
        if not response.ok:
            raise InvalidAuthentication(f"Could not authenticate '{user_id}' for organization '{self.organization}!'")
        self.search_indexes = response.json()
        return session

    @property
    def search_indexes(self):
        """Return the search indexes"""
        return self._search_indexes

    @search_indexes.setter
    def search_indexes(self, value):
        """Set the search indexes"""
        self._search_indexes = [*value]

    @property
    def _organization_url(self):
        """Returns the full organization url"""
        return f'{self.base_url}/organizations/{self.organization}'

    @property
    def nodes(self) -> dict:
        """List nodes"""
        url = f'{self._organization_url}/nodes'
        # yield from (Node(self.session, name, url) for data in self.session.get(url).json())
        yield from (Node(self.session, key, value)
                    for key, value in self.session.get(url).json().items())

    def get_node_by_name(self, name):
        """"""
        return next((node for node in self.nodes if node.name.lower() == name.lower()), None)

    def get_node_by_ip_address(self, address):
        """Use search get node by IP address"""
        node = self._search('node', f'ipaddress:{address}')
        return node

    def _search(self, index, search_string, search_filter=None, rows=1000, start=0):
        """Search chef"""

        """
        Response from server contains:
        total, start and rows (containing the data per found object)
        """
        if index not in -self.search_indexes:
            raise InvalidSearchIndex(f"'{index}' is not a valid search index!")
        params = {'q': search_string,
                  'rows': rows,
                  'start': start}
        url = f'{self._organization_url}/search/{index}'
        resp = self.session.get(url, params=params).json()
        return resp
