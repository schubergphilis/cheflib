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
Chef environment entity.

Source: https://docs.chef.io/server/api_chef_server/

Request:

GET /organizations/NAME/environments
Response

The response is similar to:

{
  "_default": "https://api.chef.io/organizations/org_name/environments/_default",
  "webserver": "https://api.chef.io/organizations/org_name/environments/webserver"
}

POST /organizations/NAME/environments
with a request body similar to:

{
  "name": "dev",
  "default_attributes": {},
  "json_class": "Chef::Environment",
  "description": "",
  "cookbook_versions": {},
  "chef_type": "environment"
}

Response

The response is similar to:

{ "uri": "https://localhost/environments/dev" }


.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from dataclasses import dataclass

from .base import Entity


@dataclass
class Environment(Entity):
    """Environment entity."""

    @property
    def description(self):
        return self.data.get('description')

    @description.setter
    def description(self, value):
        self._save_data({'description': value})

    @property
    def default_attributes(self):
        return self.data.get('default_attributes')

    @default_attributes.setter
    def default_attributes(self, value):
        self._save_data({'default_attributes': value})

    @property
    def override_attributes(self):
        return self.data.get('override_attributes')

    @override_attributes.setter
    def override_attributes(self, value):
        self._save_data({'override_attributes': value})

    @property
    def cookbook_versions(self):
        return self.data.get('cookbook_versions')

    @cookbook_versions.setter
    def cookbook_versions(self, value):
        self._save_data({'cookbook_versions': value})
