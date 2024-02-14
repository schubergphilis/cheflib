#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: __init__.py
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
cheflib package.

Import all parts from cheflib here

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

__author__ = 'Daan de Goede <ddegoede@schubergphilis.com>, Costas Tyfoxylos <ctyfoxylos@schubergphilis.com>'
__docformat__ = 'google'
__date__ = '18-01-2024'
__copyright__ = 'Copyright 2024, Daan de Goede, Costas Tyfoxylos'
__license__ = 'Apache Software License 2.0'
__maintainer__ = 'Daan de Goede, Costas Tyfoxylos'
__email__ = '<ddegoede@schubergphilis.com>, <ctyfoxylos@schubergphilis.com>'
__status__ = 'Development'  # "Prototype", "Development", "Production".

from ._version import __version__
from .cheflib import Chef
from .cheflibexceptions import (InvalidObject,
                                InvalidSearchIndex,
                                NodeNotFound)
from .entities import (Client,
                       Cookbook,
                       DataBag,
                       Environment,
                       Node,
                       Role)
# This is to 'use' the module(s), so lint doesn't complain
assert __version__
assert Chef
assert InvalidObject
assert InvalidSearchIndex
assert NodeNotFound
assert Client
assert Cookbook
assert DataBag
assert Environment
assert Node
assert Role
