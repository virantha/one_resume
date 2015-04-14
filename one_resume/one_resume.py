#!/usr/bin/env python2.7
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


"""
    OneResume - data-driven resume generation

    Usage:
        one_resume single -t <template-file> -y <yaml-file> -o <output-file> -f <format> [-v|-d]
        one_resume batch -c <config-file> [-v|-d]
        one_resume -h | --help
        one_resume --version

    Options:
        -h --help             Show this screen
        -v --verbose          Verbose logging
        -d --debug            Debug logging
        -t <template-file>    Template file (input)
        -y <yaml-file>        Resume content (YAML file)
        -o <output-file>      Output file
        -f <format>           Format (can be either Word or Text)
        -c <config-file>      Configuration file (YAML) for batch generation

"""
from __future__ import print_function
from version import __version__

import docopt
import sys, os
import logging
import yaml
from plugin import Plugin


def error(text):
    print("ERROR: %s" % text)
    sys.exit(-1)

def yaml_include(loader, node):
    # Get the path out of the yaml file
    file_name = os.path.join(os.path.dirname(loader.name), node.value)
    print (file_name)
    with file(file_name) as inputfile:
        return yaml.load(inputfile)

yaml.add_constructor("!include", yaml_include)

class OneResume(object):

    def __init__ (self):
        Plugin.load()
        self.allowed_filetypes = []
        self.allowed_formats = []
        for p, p_class in Plugin.registered.items():
            print("Registered output plugin type %s" % p)
            self.allowed_filetypes.append(p_class.template_file_extension)
            self.allowed_formats.append(p.split('Resume')[0])

    def getOptions(self, args):
        #print (args)
        self.debug = args['--debug']
        self.verbose = args['--verbose']

        if self.debug: logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        if self.verbose: logging.basicConfig(level=logging.INFO, format='%(message)s')

        if args['single']:
            self.config = yaml.load("""-
                                        data: %(-y)s
                                        outputs:
                                            - 
                                                format: %(-f)s
                                                template: %(-t)s
                                                output: %(-o)s
                                    """ % (args))
        elif args['batch']:
            config_file = args['-c']
            with open(config_file) as f:
                logging.debug("Reading configuration file %s" % config_file)
                self.config = yaml.load(f)
        else:
            assert False, "docopt command line parsing broken??"


    def run_rendering(self):
        """
            Based on self.config, instantiate each plugin conversion and run it
        """
        
        if not isinstance(self.config, list):
            # If the config was not a list, just convert this one element into a list
            self.config = [self.config]

        for i, c in enumerate(self.config):
            # For each conversion
            if not 'data' in c:
                # Check that the yaml resume file is specified
                error("Configuration file has not defined 'data' with resume yaml file")
            else:
                with open(c['data']) as resume_file:
                    self.resume = yaml.load(resume_file)

            for output in c['outputs']:
                fmt = output['format']
                # Check that we have a plugin whose classname starts with this format
                assert any([x.startswith(fmt) for x in Plugin.registered])
                template_file = output['template']
                filebasename,filetype = os.path.splitext(template_file)
                if filetype[1:] not in self.allowed_filetypes:
                    error("File type/extension %s is not one of following: %s" % (filetype,' '.join(self.allowed_filetypes)))
                output_filename = output['output']
                # Instantiate the required conversion plugin
                print ("Creating %s ..." % output_filename, end='')
                text = Plugin.registered['%sResume' % fmt](template_file, self.resume, False)
                text.render(output_filename)
                print (" done")


    def go(self, args):
        # Read the command line options, already parsed into a dict by docopt
        self.getOptions(args)
        self.run_rendering()

def main(): #pragma: no cover
    args = docopt.docopt(__doc__, version='OneResume %s' % __version__) 
    script = OneResume()
    script.go(args)

if __name__ == '__main__':
    main()

