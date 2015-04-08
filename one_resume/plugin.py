#!/usr/bin/env python2.7
# Copyright 2015 Virantha Ekanayake All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
    OneResume

        - Write your resume in YAML
        - Output it to word, html, txt, etc
"""

import logging

import imp
import pkgutil
import pkg_resources
import sys


class Plugin(object):
     
    class __metaclass__(type):
             
        def __init__(cls, name, base, attrs):
            if not hasattr(cls, 'registered'):
                cls.registered = {}
            else:
                cls.registered[name] = cls
                                     
    @classmethod
    def load(cls):
        cls.registered = {}

        for plugin in pkg_resources.iter_entry_points('one_resume.plugins'):
            plugin.load()


