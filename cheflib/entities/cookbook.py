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
Chef cookbook entity.

Source: https://docs.chef.io/server/api_chef_server/

GET /organizations/NAME/cookbooks

{
  "apache2": {
    "url": "https://localhost/cookbooks/apache2",
    "versions": [
      {"url": "https://localhost/cookbooks/apache2/5.1.0",
       "version": "5.1.0"},
      {"url": "https://localhost/cookbooks/apache2/4.2.0",
       "version": "4.2.0"}
    ]
  },
  "nginx": {
    "url": "https://localhost/cookbooks/nginx",
    "versions": [
      {"url": "https://localhost/cookbooks/nginx/1.0.0",
       "version": "1.0.0"},
      {"url": "https://localhost/cookbooks/nginx/0.3.0",
       "version": "0.3.0"}
    ]
  }
}

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from dataclasses import dataclass

from .base import Entity
from cheflib.cheflibexceptions import InvalidObject


@dataclass
class Cookbook(Entity):
    """Cookbook entity."""

    # Overriding the default data property, because
    # get result for cookbooks differs from default result
    def _post_data(self):
        if self._data is None:
            response = self._chef.session.get(self._url)
            if not response.ok:
                raise InvalidObject
            self._data = response.json()[self._name]

    @property
    def versions(self):
        return self.data.get('versions')
