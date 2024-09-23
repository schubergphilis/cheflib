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
Chef role entity.

Source: https://docs.chef.io/server/api_chef_server/

Request

GET /organizations/NAME/roles

Response

The response is similar to:

{
  "webserver": "https://chef.example/organizations/org1/roles/webserver"
}


Request

POST /organizations/NAME/roles
with a request body similar to:

{
  "name": "webserver",
  "default_attributes": {},
  "description": "A webserver",
  "env_run_lists": {
    "testenv": {
      "recipe[pegasus]"
    }
  },
  "run_list": [
    "recipe[unicorn]",
    "recipe[apache2]"
  ],
  "override_attributes": {}
}
Response

The response is similar to:

{ "uri": "https://chef.example/organizations/org1/roles/webserver" }

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from dataclasses import dataclass

from .base import Entity


@dataclass
class Role(Entity):
    """Role entity."""
