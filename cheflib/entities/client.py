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
Chef client entity.

GET: /organizations/NAME/clients
This method has no request body.
Response:
{
  "org1-validator" : "https://chef.example/orgaizations/org1/clients/org1-validator",
  "client1" : "https://chef.example/orgaizations/org1/clients/client1"
}

POST: /organizations/NAME/clients
Body:
{
  "name": "name_of_API_client",
  "clientname": "name_of_API_client",
  "validator": true,
  "create_key": true
}

DELETE: /organizations/NAME/clients/NAME
This method has no request body.
The response has no body.

GET: /organizations/NAME/clients/NAME
This method has no request body.
Response:
{
  "name": "user1",
  "clientname": "user1",
  "orgname": "test",
  "json_class": "Chef::ApiClient",
  "chef_type": "client",
  "validator": "false"
}

PUT: /organizations/NAME/clients/NAME
with a request body similar to:
{
  "name": "monkeypants",
  "validator": false
}
The response is similar to:
{
  "name": "monkeypants",
  "clientname": "monkeypants",
  "validator": true,
  "json_class":"Chef::ApiClient",
  "chef_type":"client"
}

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from dataclasses import dataclass
from typing import Dict

from cachetools import keys

from .base import (Entity,
                   EntityManager)
from .client_key import ClientKey
from cheflib.cheflibexceptions import InvalidObject


@dataclass
class Client(Entity):
    """"""
    _keys: EntityManager = None

    @property
    def expiration_date(self):
        return self.data.get('expiration_date')

    @property
    def org_name(self):
        return self.data.get('org_name')

    @property
    def private_key(self):
        return self.data.get('private_key')

    @property
    def public_key(self):
        return self.data.get('public_key')

    @property
    def validator(self):
        return self.data.get('validator')

    @property
    def _data_keys(self):
        if self._keys is None:
            # , parent_name=f'{self.name}/keys'
            self._keys = EntityManager(self._session, 'ClientKey', self._url)
        return self._keys

    @property
    def keys(self):
        return self._data_keys

    def delete_key(self, key_name: str) -> bool:
        """Delete entity"""
        if not key_name in self._keys:
            # log keyname not found!
            return False
        key = self._keys.get(key_name)
        response = self._session.delete(self._url)  # noqa
        if not response.ok:
            # log DeleteFailed(f"Failed to delete '{co.name}, reason:\n{response.text}")
            pass
        return response.ok

    def get_key_by_name(self, name: str) -> Dict:
        """Get client key by name"""
        return next(self.keys.filter(f'name:{name}'))
