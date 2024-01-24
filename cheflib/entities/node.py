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
Chef node entity.

{
  "name": "latte",
  "chef_type": "node",
  "json_class": "Chef::Node",
  "attributes": {
    "hardware_type": "laptop"
  },
  "overrides": {},
  "defaults": {},
  "run_list": [ "recipe[unicorn]" ]
}


{
    'automatic': {},
    'chef_environment': '_default',
    'chef_type': 'node',
    'default': {},
    'json_class': 'Chef::Node',
    'name': 'magweg',
    'normal': {},
    'override': {},
    'run_list': []
}

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from dataclasses import dataclass

from .base import ChefObject
import json


@dataclass
class Node(ChefObject):
    """"""

    @property
    def ip_address(self):
        return self._data.get('ip_address')

    @ip_address.setter
    def ip_address(self, value):
        self._save_data({'ip_address': value})

    @property
    def automatic(self):
        return self._data.get('automatic')

    @automatic.setter
    def automatic(self, value):
        self._save_data({'automatic': value})

    @property
    def chef_environment(self):
        return self._data.get('chef_environment')

    @chef_environment.setter
    def chef_environment(self, value):
        self._save_data({'chef_environment': value})

    @property
    def default(self):
        return self._data.get('default')

    @default.setter
    def default(self, value):
        self._save_data({'default': value})

    @property
    def normal(self):
        return self._data.get('normal')

    @normal.setter
    def normal(self, value):
        self._save_data({'normal': value})

    @property
    def override(self):
        return self._data.get('override')

    @override.setter
    def override(self, value):
        self._save_data({'override': value})

    @property
    def run_list(self):
        return self._data.get('run_list')

    @run_list.setter
    def run_list(self, value):
        self._save_data({'run_list': value})

    def create(self, name: str):
        data = {
            'name': name
        }
        self._create(data=json.dumps(data))
