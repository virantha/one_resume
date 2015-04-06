
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


# Certain portions of this file (namely the nsprefixes) are borrowed from
# the python-docx project and are provided under the following copyright:
# Copyright (c) 2009-2010 Mike MacCana

#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:

#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.


import zipfile, re
import os,shutil
from plugin import Plugin
from lxml import etree
import logging
import itertools
import copy
from collections import OrderedDict
import tempfile

from plugin import Plugin

class Word2Resume(Plugin):

    template_file_extension = 'docx'
    nsprefixes = {
    'mo': 'http://schemas.microsoft.com/office/mac/office/2008/main',
    'o':  'urn:schemas-microsoft-com:office:office',
    've': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    # Text Content
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    # Drawing
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'm':   'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'mv':  'urn:schemas-microsoft-com:mac:vml',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'v':   'urn:schemas-microsoft-com:vml',
    'wp':  'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    # Properties (core and extended)
    'cp':  'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dc':  'http://purl.org/dc/elements/1.1/',
    'ep':  'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    # Content Types
    'ct':  'http://schemas.openxmlformats.org/package/2006/content-types',
    # Package Relationships
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'pr':  'http://schemas.openxmlformats.org/package/2006/relationships',
    # Dublin Core document properties
    'dcmitype': 'http://purl.org/dc/dcmitype/',
    'dcterms':  'http://purl.org/dc/terms/'}

    char_loop_start = '<'
    char_loop_end   = '>'
    char_tag_start  = '['
    char_tag_end    = ']'

    def __init__ (self, template_file, resume_data, skip):
        self.skip = skip
        self.resume_data = resume_data
        self.template_filename = template_file

        # Open the docx file and read in the xml tree
        self.template = open (self.template_filename)
        self.doc_etree = self.read_contents(self.template)

    def render(self, output_filename):
        """
            Needs read_contents to have been called
        """
        self.substitute_data()
        self.write_and_close_docx(self.doc_etree, output_filename)

    def read_contents(self, filename):
        """
            Unzip and read the contents of the word/document.xml file

            :rtype: the contents of the file as an ElementTree
        """
        self.zipfile = zipfile.ZipFile(filename)
        xml_content = self.zipfile.read('word/document.xml')
        return etree.fromstring(xml_content)

    def _check_element_is(self, element, type_char):
        return element.tag == '{%s}%s' % (self.nsprefixes['w'],type_char)
    def _assert_element_is(self, element, type_char):
        assert self._check_element_is(element, type_char)

    def _get_all_text_in_node(self, node):
        all_txt = []
        for txt in node.itertext(tag=etree.Element):
            all_txt.append(txt)
        return ''.join(all_txt)

    def _get_parent_paragraph(self, text_node):
        self._assert_element_is(text_node, 't')
        run = text_node.getparent()
        self._assert_element_is(run, 'r')
        paragraph = run.getparent()
        self._assert_element_is(paragraph, 'p')
        return paragraph


    def _extract_loop(self, paragraph):
        """
            Find and copy the xml tree fragment that represents the '<' and '>' delimited
            loop.
        """
        inside_loop = False
        loop_tree = etree.Element("root")  # Create a new tree root
        prev_paragraph = None
        list_of_all_loop_nodes = []

        # Keep looking for the first (and only) loop after this tag
        for node, text, node_index in self._itersiblingtext(paragraph):
            if '<' in text:
                assert not inside_loop
                inside_loop = True
                loop_start_node = self._get_parent_paragraph(node)
                self._assert_element_is(loop_start_node, 'p')

            if inside_loop:
                # This text node is enclosed by a run, which is in turn enclosed by the paragraph
                # This paragraph is what we want to extract
                current_paragraph = self._get_parent_paragraph(node)
                self._assert_element_is(current_paragraph, 'p')
                if prev_paragraph != current_paragraph:
                    loop_tree.insert(node_index, copy.deepcopy(current_paragraph))
                    prev_paragraph = current_paragraph
                    list_of_all_loop_nodes.append(current_paragraph)

            if '>' in text:
                assert inside_loop
                # Done with finding loop, so exit this iterator
                break
        logging.debug("Found a loop spanning %d paragraphs, %d" % (node_index, len(loop_tree)))
        return loop_start_node, loop_tree, list_of_all_loop_nodes

    def _make_loop_instance(self, loop_tree, section_data, all_tagnames_in_section):

        # Copy the loop_tree to make an instance we can fill in with the results from 
        # the section names
        loop_instance = copy.deepcopy(loop_tree)

        for node, text, node_i in self._itersiblingtext(loop_instance):
            if '<' in text: node.text = node.text.replace('<','')
            if '>' in text: node.text = node.text.replace('>','')

            # For every node with text in it, don't even try to find a tag name
            # Instead, brute force it by trying to sub every possible tag in every node
            if node.text:
                for key in all_tagnames_in_section:
                    logging.debug("Looking for key %s" % key)
                    instance_text = section_data.get(key, '')  # Replace any key that isn't specified for this instance with a blank
                    node.text = node.text.replace('['+key+']', str(instance_text))
        return loop_instance

    def _fill_in_section(self, section_etree, section_list):
        """
            section_list is a list of dicts containing the contents for the current section. For example:
                
                [
                 { key1:val1, key2:val2 },
                 { key1:val1, key2:val2, key3:val3},
                ]

            Assumptions:
                - All loop starts are in their own paragraphs
                - loops can span multiple paragraphs
                - Any content after the loop must be in different paragraph
                - No tables anywhere!
        """
        # Get the parent paragraph 
        paragraph = self._get_parent_paragraph(section_etree)

        # Build up a copy of the loop sub-tree in loop_tree. We will instance this as many times as needed.
        # Also, keep track of all the elements belonging to the loop body in elements_to_delete
        # so that we can delete the original loop definition once we are done instancing the loop.
        loop_start_node, loop_tree, elements_to_delete = self._extract_loop(paragraph)
        
        # Max possible set of subtags
        all_tag_names_in_section = self._get_all_keys_in_list_of_dicts(section_list)

        # Iterate and create the loop with the section data
        loop_instance = []
        for section_data in section_list:
            loop_instance.append(self._make_loop_instance(loop_tree, section_data, all_tag_names_in_section))

        # Now, add the loop_instance to the body
        body = loop_start_node.getparent()
        index_to_insert_at = body.index(loop_start_node)+1
        logging.debug("Inserting at index %d, %d instances" % (index_to_insert_at, len(loop_instance)))
        for inst in loop_instance:
            for child in inst.getchildren():
                body.insert(index_to_insert_at, child)
                index_to_insert_at += 1

        # Delete the loop template
        for e in elements_to_delete:
            body.remove(e)

        # Remove a section heading name if it's preceded with a bang (for example, a contact section, where
        # we don't need to title the section
        if '[!' in section_etree.text:
            paragraph.getparent().remove(paragraph)

    def _find_sections(self, my_etree, tags_to_find, char_to_stop_on=None):
        """
            Build a dict of all the top-level tags in the document and the corresponding
            text node.

            Also replace the top level tag header with the section name

            :rtype: Dict of tag name -> xml node
            
        """

        tags = {}
        logging.debug("Looking for tags: %s" % (','.join(tags_to_find)))
        mTag = r"""\[\!?(?P<tag>[\s\w\_\|]+)\]"""
        # lowercase all the tags_to_find, just in case the user upper-cased some of them
        tags_to_find = [x.lower() for x in tags_to_find]

        for node,text in self._itertext(my_etree):
            tag_text = re.findall(mTag, text) 
            if tag_text:
                logging.debug("Found grps %s" % (','.join(tag_text)))
            for tag in tag_text:
                tag_lower = tag.lower()
                tag_lower = tag_lower.split('|')[0]
                if tag_lower in tags_to_find:
                    tags[tag_lower] = node
                    # Replace the brackets with nothing
                    if '[!' in node.text:
                        #node.text = node.text.replace('[!'+tag+']', 'lsdjflkd')
                        body = node.getparent().getparent().getparent()
                        #body.remove(node.getparent().getparent())
                    else:
                        node.text = node.text.replace('['+tag+']', tag)
                        if '|' in node.text:
                            # We have alternate text so just use that
                            # FIXME:  This is wrong, we need to sub out the text, and not replace the whole node!
                            node.text = node.text.split('|')[1]

        return tags

    def _get_all_keys_in_list_of_dicts(self, mylist):
        mykeys = set()
        for e in mylist:
            for k in e.keys():
                mykeys.add(k)
        return list(mykeys)

    def substitute_data(self):

        body = self.doc_etree.xpath('/w:document/w:body', namespaces=self.nsprefixes)[0]
        self.collapse_tags(body)

        if self.skip:
            return

        # Get a list of all the top-level tags
        sections = self._find_sections(self.doc_etree, self.resume_data.keys())
        for section_name, section_node in sections.items():
            logging.debug("Subtag search for %s" % section_name)
            self._fill_in_section(section_node, self.resume_data[section_name])
            logging.debug("Finished find_subtags_in_loop")
        return

    def _itertext(self, my_etree):
        """Iterator to go through xml tree's text nodes"""
        for node in my_etree.iter(tag=etree.Element):
            if self._check_element_is(node, 't'):
                yield (node, node.text)

    def _itersiblingtext(self, my_etree):
        """Iterator to go through xml tree sibling text nodes"""
        # First, check if there are siblings, if not, we need to just go through the current element
        if my_etree.getnext() is None:
            for node in my_etree.iter(tag=etree.Element):
                if self._check_element_is(node, 't'):
                    yield (node, node.text, 0)
        else:
            for i, sib in enumerate(my_etree.itersiblings(tag=etree.Element)):
                for node in sib.iter(tag=etree.Element):
                    if self._check_element_is(node, 't'):
                        yield (node, node.text, i)


    def collapse_tags(self, my_etree):
        """
            Find the special tags and collapse all the text in them to one single paragraph. This
            method works in-place, modifying the passed in etree.
            This works because we know there shouldn't be any formatting inside the tag name.


            :rtype: Nothing
        """
        chars = []
        is_tag_start = False      # True if inside tag
        tag_start_node = None     # Pointer to current node. 
        tag_start_char = '['
        tag_end_char = ']'

        # For every node with text
        for node,text in self._itertext(my_etree):
            # Go through each node's text character by character
            for i,c in enumerate(text):
                if c == tag_start_char:  # Tag is starting!
                    assert not is_tag_start  # Better not already be inside a tag!
                    is_tag_start = True 
                    tag_start_node = node 
                    chars = []
                elif c == tag_end_char:  # Tag is ending
                    assert is_tag_start  # Better have seen a tag start!
                    is_tag_start = False
                    # If tag_start_node is the same as current node, then we don't need to do anything
                    # But otherwise:
                    if node != tag_start_node:
                        # Tag started in different node, so move all the chars we've encountered since then
                        # to the tag_start_node
                        chars.append(c)
                        tag_start_node.text += ''.join(chars)
                        node.text = text[i+1:]   # Remove characters from this node
                else:
                    # Normal text character
                    if is_tag_start and node != tag_start_node:
                        # Need to save these chars to append to text in openbrac_node
                        chars.append(c)

            # If we're here, that means we've consumed all the text in the current node.
            # Check if this node was part of a tag, yet did not start the tag
            if is_tag_start and node!= tag_start_node:
                # Need to remove this text completely as we've saved all of it inside chars for moving
                # into the start_node
                node.text = ""


    def write_and_close_docx (self, xml_content, output_filename):
        """ Create a temp directory, expand the original docx zip.
            Write the modified xml to word/document.xml
            Zip it up as the new docx
        """

        tmp_dir = tempfile.mkdtemp()

        self.zipfile.extractall(tmp_dir)

        with open(os.path.join(tmp_dir,'word/document.xml'), 'w') as f:
            xmlstr = etree.tostring (xml_content, pretty_print=True)
            f.write(xmlstr)

        # Get a list of all the files in the original docx zipfile
        filenames = self.zipfile.namelist()

        # Now, create the new zip file and add all the filex into the archive
        zip_copy_filename = output_filename
        with zipfile.ZipFile(zip_copy_filename, "w") as docx:
            for filename in filenames:
                docx.write(os.path.join(tmp_dir,filename), filename)

        # Clean up the temp dir
        shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    script = WordAPI('test/blah.docx', {}, False)
    print (etree.tostring(script.doc_etree, pretty_print=True))
    script.collapse_tags(script.doc_etree)
    print (etree.tostring(script.doc_etree, pretty_print=True))


