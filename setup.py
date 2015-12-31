#!/usr/bin/env python
from distutils.core import setup, Extension

webfaction_classifiers = [
"Programming Language :: Python :: 2",
"Programming Language :: Python :: 3",
"Intended Audience :: Developers",
"License :: OSI Approved :: MIT License",
"Topic :: Software Development :: Libraries",
"Topic :: Utilities",
"Topic :: Software Development :: Libraries :: Application Frameworks",
]

long_description = """Command-line tool and library for the WebFaction API
https://docs.webfaction.com/xmlrpc-api/

Uses a Python XML-RPC instance to communicate with the Webfaction API. Most API commands have been turned into Python commands
"""

setup(
    name='webfaction',
    description='Webfaction Python API',
    long_description=long_description,
    url="https://github.com/tclancy/Webfaction-Python-API",
    author="Patrick Robertson",
    author_email="webfaction-python@patjack.uk",
    license="MIT",
    packages=['webfaction'],
    platforms=["all"],
    version="1.0",
    scripts=['bin/webfaction'],
    install_requires=['configobj',],
    classifiers=webfaction_classifiers,
)
