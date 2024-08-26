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
Chef data bag entity.

GET: /organizations/NAME/data
{
  "users": "https://chef.example/organizations/NAME/data/users",
  "applications": "https://chef.example/organizations/NAME/data/applications"
}

POST: /organizations/NAME/data
{
  "name": "users"
}

GET: /organizations/NAME/data/NAME/ITEM
{
  "real_name": "Adam Jacob",
  "id": "adam"
}


.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from dataclasses import dataclass
from typing import Optional

from .databagitem import DataBagItem
from .base import Entity


@dataclass
class DataBag(Entity):
    """"""
    @property
    def get_item_names(self):
        return self.data.keys()

    def get_item_by_name(self, name: str, secret: bytes = None) -> [DataBagItem, None]:
        """"""
        url = self.data.get(name, None)
        if not url:
            # TODO log invalid name
            return None
        return DataBagItem(self._chef, name, url, _secret=secret)

    def create_item(self, name, data, secret=None) -> Optional[DataBagItem]:
        """"""
        body = {'id': name}
        response = self._chef.session.post(self._url, json=body)
        if not response.ok:
            # log shizzle
            return None
        db_item = DataBagItem(self._chef, name, f'{self._url}/{name}')
        db_item.secret = secret
        db_item.data = data
        return db_item
