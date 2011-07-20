from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup
from xml2json import __version__

setup(
    name = "xml2json",
    version = __version__,
    author = "Andrea Cisternino",
    author_email = "a.cisternino@gmail.com",
    description = "Converts XML documents to JSON data structures",
    long_description = open("README.rst").read(),
    install_requires = [ "lxml >= 2.3" ],
    py_modules = [ "xml2json" ],
    url = "http://github.com/acisternino/xml2json",
    license = "See LICENSE.txt",
    test_suite = "tests",
    keywords = "xml json",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Markup :: XML",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"
    ]
)

