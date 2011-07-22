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

"""Module description
"""

__version__ = "0.1dev"
__author__ = [ "Andrea Cisternino <a.cisternino@gmail.com>" ]
__license__ = "MIT"

import collections

from lxml import etree

__all__ = ( "OrderedMultiMap" , "parse_root", "parse_element" )

#---- OrderedMultiMap --------------------------------------

class OrderedMultiMap(collections.OrderedDict):
    """A simple OrderedMultiMap that uses lists only when needed.
    """

    def __setitem__(self, key, value):
        if key not in self:
            super(OrderedMultiMap, self).__setitem__(key, value)
        else:
            if isinstance(self[key], list):
                self[key].append(value)
            else:
                tmp = self[key]
                super(OrderedMultiMap, self).__setitem__(key, [ tmp, value ])

    def attr(self, key):
        if "__attr__" in self:
            return self.get("__attr__").get(key)

    def ns(self):
        return self.get("__ns__")

    def body(self):
        return self.get("__body__")

    def __getattr__(self, attr):
        if attr in self:
            return self.get(attr)
        return super(OrderedMultiMap, self).__getattr__(attr)

#---- _build_json -----------------------------------------------

##
# Generates a JSON compatible data structure from an XML element recursively.
# This version uses explict keys to identify the element content, namespace and
# attributes.
#
# @param element The element to convert.
# @param dictionary The top-level dictionary used to contain the xml element information.
# @param dump_ns Wether to add namespace information to the document.

def _build_json(element, dictionary, dump_ns=True):
    """Converts an lxml.etree.Element instance to a JSON data structure
       containing the same information.
    """
    qn = etree.QName(element.tag)

    tmp = dictionary[qn.localname] = OrderedMultiMap()

    # element namespace
    if dump_ns and qn.namespace:
        tmp["__ns__"] = qn.namespace

    # xml attributes
    if element.items():
        tmp["__attr__"] = dict(element.items())

    # content
    if element.text and not element.text.isspace():
        # leaf element with data
        tmp["__body__"] = element.text

    elif len(element) > 0:
        # container element
        tmp["__body__"] = OrderedMultiMap()

        for child in element:
            # recurse into children
            _build_json(child, tmp["__body__"])

    else:
        # element with text and children, not allowed
        pass

#---- parse_root() ----------------------------------------------

##
# Parses the root element of the XML document.
#
# @param source A filename or file object containing XML data.
# @return An OrderedMultiMap containing information on the root element
# @defreturn OrderedMultiMap

def parse_root(source):
    """Parses the root element of an XML document.
    """
    for event, elem in etree.iterparse(source, events=("start", )):

        qn = etree.QName(elem.tag)

        # very first event: start of root element, collect general info and exit
        if event == "start":

            # "root" key contains the local name of the root element
            doc = OrderedMultiMap({ "root": qn.localname })

            doc[qn.localname] = body = OrderedMultiMap()

            # the "schema" key contains the namespace URI of the root element
            if qn.namespace:
                body["schema"] = qn.namespace

            # fix default namespace bad key
            if elem.nsmap:
                nsmap = OrderedMultiMap(elem.nsmap)
                if None in nsmap:
                    nsmap["__default__"] = nsmap[None]
                    del nsmap[None]
                body["nsmap"] = nsmap

            # root element attributes
            if elem.attrib:
                body["attr"] = OrderedMultiMap(elem.attrib)

            return doc

#---- parse_element() -------------------------------------------

##
# Parses and converts to JSON the specified elements of the XML document.
#
# @param func A callback function that will be called with the JSON data
#             structure as input.
# @param source A filename or file object containing XML data.
# @param element The fully qualified name of the XML element that we want to convert.
# @param dump_ns Wether to add namespace information to the resulting document.
# @param jsonifier A callback function that can convert the sliced lxml.etree.Element
#                  into a complete JSON structure.
# @return The number of slices processed.

def parse_element(func, source, element, dump_ns=True, jsonifier=_build_json):
    """Parses and converts to JSON a specified element in an XML document.
    """
    slice_tag = etree.QName(element)
    slices = 0

    for event, elem in etree.iterparse(source, tag = slice_tag):
        # we only receive "end" events for the desired element

        doc = OrderedMultiMap()

        # convert Element to JSON
        jsonifier(elem, doc)

        # do something with fragment
        try:
            func(doc)
        except TypeError:
            print "function %s is not callable" % func
            raise

        slices += 1

    return slices
