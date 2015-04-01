
# Copyright 2013 Virantha Ekanayake All Rights Reserved.
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

import logging
from mako.template import Template
from textwrap import TextWrapper
from plugin import Plugin

class TextResume(Plugin):

    template_file_extension = 'mako'

    def __init__ (self, template_file, resume_data, skip):
        self.skip = skip
        self.resume_data = resume_data
        self.template_filename = template_file
        self.indent_spaces = 2

    def render(self, output_filename):
        with open(output_filename, "w") as output_file:
            txt = self._get_rendered_text()
            output_file.write(txt)

    def _get_rendered_text(self):
        with open(self.template_filename) as tmpl_file:
            tmpl_text = tmpl_file.read()
        tmpl = Template(tmpl_text)
        txt =  tmpl.render(d=self.resume_data, s=self)
        logging.debug(txt)
        return txt
        

    def _wrap(self, indent, s, width=70):
        indent_str = "  " * indent
        t = TextWrapper( width=width, subsequent_indent = indent_str)
        return '\n'.join(t.wrap(s))
            


