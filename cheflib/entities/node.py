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

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from dataclasses import dataclass

from .base import ChefObject


@dataclass
class Node(ChefObject):
    """"""

    @property
    def ip_address(self):
        return self._data.get('ip_address')

    @ip_address.setter
    def ip_address(self, value):
        self._save_data({'ip_address': value})

    def update_attributes(self, attrs):
        self._data.update(attrs)
        self._save_data(self._data)

    @property
    def attributes(self):
        return self._get_attributes()

    def _get_attributes(self):
        self._session.get(self.url)

