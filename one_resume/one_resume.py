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
    OneResume

        - Write your resume in YAML
        - Output it to word, html, txt, etc
"""
from __future__ import print_function

import argparse
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

    def getOptions(self, argv):
        p = argparse.ArgumentParser(prog="oneresume.py")

        p.add_argument('-d', '--debug', action='store_true',
            default=False, dest='debug', help='Turn on debugging')

        p.add_argument('-v', '--verbose', action='store_true',
            default=False, dest='verbose', help='Turn on verbose mode')
        p.add_argument('-s', '--skip-substitution', action='store_true',
            default=False, dest='skip', help='Skip the text substitution and just write out the template as is (useful for pretty-printing')

        # Now split up the options on whether we just run one template rendering
        # or use a "batch" mode to read a yaml config file to run multiple
        subparsers = p.add_subparsers(help="Type of processing to run",
                                        dest = "subparser_name")

        parser_singlefile = subparsers.add_parser('single', help='Run a single conversion')
        parser_singlefile.add_argument('-t', '--template-file', required=True, 
            help='Template filename %s' % self.allowed_filetypes)
        parser_singlefile.add_argument('-y', '--yaml-resume-file', required=True, 
            help='Resume yaml filename')
        parser_singlefile.add_argument('-o', '--output-file', required=True, 
            help='Output filename')
        parser_singlefile.add_argument('-f', '--format', required=True, 
            choices = self.allowed_formats,
            help='Conversion type %s' % self.allowed_formats )


        parser_configfile = subparsers.add_parser('batch', help="Run multiple conversions using a yaml config file as input")
        parser_configfile.add_argument('-c', '--config-file', required=True, type=argparse.FileType('r'),
             help='configuration YAML filename ' )


        args = p.parse_args(argv)

        self.debug = args.debug
        self.verbose = args.verbose
        self.skip = args.skip

        if args.debug:
            logging.basicConfig(level=logging.DEBUG, format='%(message)s')

        if args.verbose:
            logging.basicConfig(level=logging.INFO, format='%(message)s')

        # Normal options
        if args.subparser_name == 'single':
            self.config = yaml.load("""-
                                        data: %s
                                        outputs:
                                            - 
                                                format: %s
                                                template: %s
                                                output: %s
                                    """ % (args.yaml_resume_file, args.format, args.template_file, args.output_file ))
        else:
            config_file = args.config_file
            logging.debug("Reading configuration file %s" % config_file)
            self.config = yaml.load(config_file)
            config_file.close()

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
                text = Plugin.registered['%sResume' % fmt](template_file, self.resume, self.skip)
                text.render(output_filename)
                print (" done")


    def go(self, argv):
        # Read the command line options
        self.getOptions(argv)
        self.run_rendering()

def main(): #pragma: no cover
    script = OneResume()
    script.go(sys.argv[1:])

if __name__ == '__main__':
    main()

