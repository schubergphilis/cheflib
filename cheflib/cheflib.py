#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: cheflib.py
#
# Copyright 2024 Daan de Goede
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
Main code for cheflib.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

import logging

__author__ = '''Daan de Goede <ddegoede@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''18-01-2024'''
__copyright__ = '''Copyright 2024, Daan de Goede'''
__credits__ = ["Daan de Goede"]
__license__ = '''Apache Software License 2.0'''
__maintainer__ = '''Daan de Goede'''
__email__ = '''<ddegoede@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''cheflib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())
