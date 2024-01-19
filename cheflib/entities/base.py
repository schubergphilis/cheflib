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
Chef base entity.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from dataclasses import dataclass
from typing import Dict, Optional

from chefsessionlib import ChefSession

from cheflib.cheflibexceptions import InvalidObject


@dataclass
class ChefObject:
    _session: ChefSession
    _name: str
    _url: str
    _data: Optional[Dict] = None

    @property
    def data(self):
        if self._data is None:
            response = self._session.get(self._url)
            if not response.ok:
                raise InvalidObject
            self._data = response.json()
        return self._data

    @property
    def name(self):
        return self.data.get('name')

    @name.setter
    def name(self, value):
        self._save_data({'name': value})

    def _save_data(self, data):
        url = 'me/name'
        self._session.put(url, data=data)
