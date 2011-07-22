========
xml2json
========
:Info: xml2json is a module that parses XML files and converts them to JSON
:Author: Andrea Cisternino (http://github.com/acisternino)

About
=====

xml2json is a Python module that provides functionality to parse XML
files or fragments and converts them to a JSON data structure.

The purpose of xml2json is to add a very thin layer on top of `lxml <http://lxml.de>`_
that helps in parsing large data-driven XML files incrementally, converting
each *segment* to a JSON data structure for further processing.

The reason for generating JSON comes from the first use case for this module
that required feeding data extracted from the XML files to
`MongoDB <http://www.mongodb.org>`_.

Installation
============

If you have `setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
you can use ``easy_install -U xml2json``. Otherwise, you can download the
source from `GitHub <http://github.com/acisternino/xml2json>`_ and run
``python setup.py install``.

Dependencies
============

- lxml 2.3+

Using xml2json
==============

The xml2json module exports two functions and an enhanced ``dict()`` class
that better support the creation of a JSON data structure.

Parsing the root element: ``parse_root()``
------------------------------------------

The root element of a data-driven XML file typically contains important
information about the document. Namespace declarations, for example, can
contain a schema version embedded in the namespace URI and other attributes
can be useful when parsing the rest of the file.

To get hold of this information before the actual parsing begins I decided
to create a function that only parses the root element and returns all
its information encoded as a JSON document.

For this document::

  <RootEl xmlns="urn:example.org:fakedoc.v02" xmlns:a="urn:example.org:fakedoc.v02:sub" processing="full">
    ...
  </RootEl>

``parse_root()`` returns::

  {
    "root": "RootEl",
    "RootEl": {
      "schema": "urn:example.org:fakedoc.v02",
      "nsmap": {
        "a": "urn:example.org:fakedoc.v02:sub",
        "__default__": "urn:example.org:fakedoc.v02"
      },
      "attr": {
        "processing": "full"
      }
    }
  }

The ``"root"`` key contains the local name of the root element (i.e. without
namespace)

The only other key contained in the Map is the tag local name itself and
its value is a structure with the following keys:

schema
  This optional key ha a string value with the namespace URI of the root
  element if present.

nsmap
  This map contains a number of key, value pairs where keys are the prefixes
  used in the document and values are the corresponding namespace URI's.
  
  The ``"__default__"`` key duplicates the information already provided by the
  ``"schema"`` entry.
  
attr
  This key contains a Map with all the attributes of the element with their
  values.
