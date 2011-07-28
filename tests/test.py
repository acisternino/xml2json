#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, Andrea Cisternino <a.cisternino@gmail.com>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import unittest, StringIO

from xml2json import *

class RootElementTests(unittest.TestCase):

    def test_non_xml(self):
        """non-xml file throws XMLSyntaxError
        """
        from lxml.etree import XMLSyntaxError
        with self.assertRaises(XMLSyntaxError):
            parse_root(StringIO.StringIO("This is not XML"))

    def test_malformed_xml(self):
        """parse_root() with malformed file
        """
        from lxml.etree import XMLSyntaxError
        with self.assertRaises(XMLSyntaxError):
            parse_root(StringIO.StringIO("<r>"))

    def test_simple_root(self):
        """parse_root() with minimal file 1
        """
        root_el = parse_root(StringIO.StringIO("<r></r>"))
        self.assertEqual(root_el.root, "r")

    def test_simple_root_inner_doc(self):
        """parse_root() with minimal file 2
        """
        root_el = parse_root(StringIO.StringIO("<r></r>"))
        self.assertIn("r", root_el)

    def test_root_with_namespace(self):
        """parse_root() with namespace
        """
        root_el = parse_root(StringIO.StringIO('<r xmlns="urn:a"></r>'))
        root_el_name = root_el.root
        self.assertEqual(root_el[root_el_name].schema, u"urn:a")

    def test_root_with_nsmap(self):
        """parse_root() with more than one namespace
        """
        root_el = parse_root(StringIO.StringIO('<r xmlns="urn:a" xmlns:b="urn:b"></r>'))
        root_el_name = root_el["root"]
        nsmap = root_el[root_el_name].nsmap
        self.assertEqual(nsmap.__default__, u"urn:a")
        self.assertEqual(nsmap.b, u"urn:b")

    def test_root_with_children(self):
        """parse_root() with children
        """
        root_el = parse_root(StringIO.StringIO('<r xmlns="urn:a" xmlns:b="urn:b"><a/><b:b><b:c/></b:b></r>'))
        root_el_name = root_el["root"]
        nsmap = root_el[root_el_name].nsmap
        self.assertEqual(nsmap.__default__, u"urn:a")
        self.assertEqual(nsmap.b, u"urn:b")


class SliceElementTests(unittest.TestCase):
    
    def test_non_xml(self):
        """non-xml file throws XMLSyntaxError
        """
        from lxml.etree import XMLSyntaxError
        def cb_func(json_elem):
            pass
        with self.assertRaises(XMLSyntaxError):
            parse_element(cb_func, StringIO.StringIO("This is not XML"), "dummy")

    def test_leaf_element(self):
        """slice element in document is a leaf
        """
        def cb_func(json_elem):
            self.assertEqual(len(json_elem), 1)
            self.assertEqual(json_elem.a.body(), "TEST")
        parse_element(cb_func, StringIO.StringIO('<r><a>TEST</a></r>'), "a")

    def test_simple_hierachy(self):
        """very simple hierarchy
        """
        def cb_func(json_elem):
            self.assertEqual(len(json_elem), 1)
            self.assertEqual(len(json_elem.a.body()), 2)
            self.assertEqual(json_elem.a.body().b.body(), "LINE_B")
        parse_element(cb_func, StringIO.StringIO('<r><a><b>LINE_B</b><c>LINE_C</c></a></r>'), "a")

    def test_simple_hierachy_with_ns(self):
        """very simple hierarchy with namespaces
        """
        def cb_func(json_elem):
            self.assertEqual(len(json_elem), 1)
            self.assertEqual(json_elem.a.ns(), "urn:a")
            self.assertEqual(json_elem.a.body().b.body(), "LINE")
        parse_element(cb_func, StringIO.StringIO('<r xmlns:nsa="urn:a"><nsa:a><nsa:b>LINE</nsa:b></nsa:a></r>'), "{urn:a}a")

    def test_simple_hierachy_repeated(self):
        """very simple hierarchy with repeated elements
        """
        def cb_func(json_elem):
            self.assertEqual(len(json_elem), 1)
            self.assertEqual(len(json_elem.a), 1)
            self.assertEqual(len(json_elem.a.body().b), 2)
            self.assertEqual(json_elem.a.body().b[1].body(), "LINE2")
        parse_element(cb_func, StringIO.StringIO('<r><a><b>LINE1</b><b>LINE2</b></a></r>'), "a")

    def test_attributes(self):
        """element attributes
        """
        def cb_func(json_elem):
            self.assertEqual(len(json_elem), 1)
            self.assertEqual(json_elem.a.body().c.attr("att"), "val")
        parse_element(cb_func, StringIO.StringIO('<r><a><b>LINE_B</b><c att="val">LINE2</c></a></r>'), "a")

    def test_attributes_on_repeated_elems(self):
        """element attributes on repeated elements
        """
        def cb_func(json_elem):
            self.assertEqual(len(json_elem), 1)
            self.assertEqual(json_elem.a.body().b[1].attr("att"), "val")
        parse_element(cb_func, StringIO.StringIO('<r><a><b>LINE_B</b><b att="val">LINE2</b></a></r>'), "a")
