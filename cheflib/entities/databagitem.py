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

Source: https://docs.chef.io/server/api_chef_server/

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
from copy import deepcopy
from dataclasses import dataclass
from typing import Optional, Dict

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from base64 import b64decode, b64encode
import json
import logging
import textwrap

from .base import Entity

# This is the main prefix used for logging
LOGGER_BASENAME = 'base'
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


json_k = ['iv', 'encrypted_data', 'auth_tag']


# because ruby b64encode does this by default
def b64_chunker(b64: str) -> str:
    return '\n'.join(textwrap.wrap(b64, 60)) + '\n'


def _is_encrypted(data) -> bool:
    encrypted = False
    for k in data.keys():
        if 'version' in data[k]:
            if data[k]['version'] == 3:
                encrypted = True
            elif data[k]['version'] in [1, 2]:
                LOGGER.info('Problem decrypting, we do not support version 1 and 2')
    return encrypted


def _decrypt_item(data, secret) -> dict:
    key = SHA256.new(secret).digest()
    db_item = {'id': data['id']}
    try:
        for item_key in data.keys():
            if item_key == 'id':
                continue
            json_v = {k: b64decode(data[item_key][k]) for k in json_k}
            cipher = AES.new(key=key, mode=AES.MODE_GCM, nonce=json_v['iv'])
            result = cipher.decrypt_and_verify(json_v['encrypted_data'], json_v['auth_tag'])
            db_item[item_key] = json.loads(result)
    except (ValueError, KeyError):
        LOGGER.info('Decryption failed, maybe the wrong secret was provided?')
    return db_item


def _encrypt_item(data, secret) -> dict:
    key = SHA256.new(secret).digest()
    db_item = {'id': data['id']}
    try:
        for item_key in data.keys():
            if item_key == 'id':
                continue
            cipher = AES.new(key, AES.MODE_GCM)
            encrypted_data, auth_tag = cipher.encrypt_and_digest(json.dumps(data[item_key]).encode())
            json_v = [b64_chunker(b64encode(x).decode('utf-8')) for x in (cipher.nonce, encrypted_data, auth_tag)]
            db_item[item_key] = dict(zip(json_k, json_v))
            db_item[item_key].update({'version': 3, 'cipher': 'aes-256-gcm'})
    except (ValueError, KeyError):
        LOGGER.info("Encryption failed, maybe an invalid secret was provided?")
    return db_item


@dataclass
class DataBagItem(Entity):
    _secret: Optional[bytes] = None
    _encrypted_data: Optional[dict] = None

    def _pre_save_data(self, data: Dict) -> Dict:
        """If secret is given, encrypt item."""
        if self._secret:
            return _encrypt_item(data, self._secret)
        return data

    def _post_data(self):
        """Decrypt item is item is encrypted and secret is given."""
        self._encrypted = False
        self._encrypted_data = None
        if _is_encrypted(self._data):
            self._encrypted = True
            self._encrypted_data = deepcopy(self._data)
        if self._secret and _is_encrypted(self._data):
            self._data = _decrypt_item(self._data, self._secret)

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, secret):
        self._secret = secret

    @property
    def encrypted(self):
        return self._encrypted
