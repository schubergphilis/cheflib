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
from typing import Dict, Optional

from .base import Entity
from .client_key import ClientKey


@dataclass
class Client(Entity):
    """"""
    _keys: Optional[Dict] = None

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
    def keys(self):
        url = f'{self._url}/keys'
        response = self._chef.session.get(url)
        if not response.ok:
            self._logger.debug(f'Unable to retrieve Keys url: "{url}", reason: "{response.text}"')
            return None
        yield from (ClientKey(self._chef, key['name'], key['uri']) for key in response.json())

    def create_key(self, name, data) -> Optional[ClientKey]:
        """"""
        body = {'name': name}
        body.update(data)
        response = self._chef.session.post(f'{self._url}/keys', json=body)
        if not response.ok:
            self._logger.debug(f'Key creation failed, body: "{body}", reason: "{response.text}"')
            return None
        response_data = response.json()
        self._keys = None
        return ClientKey(self._chef, name, response_data['uri'])

    def get_key_by_name(self, name: str) -> ClientKey:
        """Get client key by name."""
        return next((client_key for client_key in self.keys if client_key.name.lower() == name.lower()), None)

    def delete_key_by_name(self, name: str) -> bool:
        """Delete client key by name."""
        key = self.get_key_by_name(name)
        self._keys = None
        return key.delete()

    def reregister(self) -> bool:
        # TODO this is not working in the current API, needs attention
        # http_api.put("clients/#{name}", name: name, admin: admin, validator: validator, private_key: true )
        data = {'name': self.name, 'validator': self.validator, 'create_key': True}
        response = self._chef.session.put(self._url, json=data)
        if not response.ok:
            self._logger.info(response.text)
        return response.ok
