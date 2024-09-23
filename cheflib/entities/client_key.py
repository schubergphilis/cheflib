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
Chef client key entity.

Source: https://docs.chef.io/server/api_chef_server/

GET: /organizations/NAME/clients/NAME/keys
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
from datetime import datetime
from .base import Entity


@dataclass
class ClientKey(Entity):
    """Client key entity."""

    @property
    def public_key(self):
        """Return public key or None."""
        return self.data.get('public_key')

    @property
    def expiration_date(self):
        """Return the expiration date of the key or None."""
        return self.data.get('expiration_date')

    @property
    def expired(self):
        """Returns true if key is expired."""
        if self.expiration_date == 'infinity':
            return False
        datetime_format = '%Y-%m-%dT%H:%M:%SZ'
        expiration_timestamp = datetime.strptime(self.expiration_date, datetime_format)
        current_timestamp = self._chef.get_current_timestamp()
        return expiration_timestamp < current_timestamp
