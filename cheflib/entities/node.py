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

from .base import Entity


@dataclass
class Node(Entity):
    """"""

    @property
    def ip_address(self):
        return self.data.get('ip_address')

    @property
    def automatic(self):
        return self.data.get('automatic')

    @property
    def chef_environment(self):
        return self.data.get('chef_environment')

    @chef_environment.setter
    def chef_environment(self, value):
        self._save_data({'chef_environment': value})

    @property
    def default(self):
        return self.data.get('default')

    @property
    def normal(self):
        return self.data.get('normal')

    @normal.setter
    def normal(self, value):
        self._save_data({'normal': value})

    @property
    def override(self):
        return self.data.get('override')

    @property
    def run_list(self):
        return self.data.get('run_list')

    @run_list.setter
    def run_list(self, value):
        self._save_data({'run_list': value})
