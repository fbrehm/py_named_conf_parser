#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from distutils.core import setup, Command

# own modules:
cur_dir = os.getcwd()
if sys.argv[0] != '' and sys.argv[0] != '-c':
    cur_dir = os.path.dirname(sys.argv[0])

libdir = os.path.join(cur_dir, 'src')
module = os.path.join(libdir, 'named_conf_parser.py')
if os.path.isdir(libdir) and os.path.isfile(module):
    sys.path.insert(0, os.path.abspath(libdir))
del module
del libdir
del cur_dir

import named_conf_parser

packet_version = named_conf_parser.__version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'named-conf-parser',
    version = packet_version,
    description = 'Module for a class parsing the named.conf of BIND',
    long_description = read('README.txt'),
    author = 'Frank Brehm',
    author_email = 'frank.brehm@profitbricks.com',
    url = 'ssh://git.profitbricks.localdomain/srv/git/python/named-conf-parser.git',
    license = 'LGPLv3+',
    platforms = ['posix'],
    package_dir = {'': 'src'},
    py_modules = [
        'named_conf_parser',
    ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    requires = [
        'pb_base (>= 0.3.10)',
    ]
)

#========================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 expandtab
