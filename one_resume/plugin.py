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


class Plugin(object):
     
    class __metaclass__(type):
             
        def __init__(cls, name, base, attrs):
            if not hasattr(cls, 'registered'):
                cls.registered = {}
            else:
                #cls.registered.append(cls)
                cls.registered[name] = cls
                                     
    @classmethod
    def load(cls, *paths):
        paths = list(paths)
        cls.registered = {}
        for _, name, _ in pkgutil.iter_modules(paths):
            fid, pathname, desc = imp.find_module(name, paths)
            try:
                imp.load_module(name, fid, pathname, desc)
            except Exception as e:
                logging.warning("could not load plugin module '%s': %s",
                                pathname, e.message)
            if fid:
                fid.close()

