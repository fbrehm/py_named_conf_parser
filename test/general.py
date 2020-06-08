#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2020 Frank Brehm, Berlin
@license: GPL3
@summary: general used functions an objects used for unit tests on
          the ISC- and Named-Conf python modules
"""
from __future__ import print_function

import os
import sys
import logging
from logging import Formatter
import argparse

try:
    import unittest2 as unittest
except ImportError:
    import unittest

if sys.version_info[0] != 3:
    print("This script is intended to use with Python3.", file=sys.stderr)
    print("You are using Python: {0}.{1}.{2}-{3}-{4}.\n".format(
        *sys.version_info), file=sys.stderr)
    sys.exit(1)

if sys.version_info[1] < 4:
    print("A minimal Python version of 3.4 is necessary to execute this script.", file=sys.stderr)
    print("You are using Python: {0}.{1}.{2}-{3}-{4}.\n".format(
        *sys.version_info), file=sys.stderr)
    sys.exit(1)

# Own modules
from fb_tools.colored import ColoredFormatter


#==============================================================================

LOG = logging.getLogger(__name__)

#==============================================================================
def get_arg_verbose():

    arg_parser = argparse.ArgumentParser()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-v", "--verbose", action = "count",
            dest = 'verbose', help = 'Increase the verbosity level')
    args = arg_parser.parse_args()

    return args.verbose

#==============================================================================
def init_root_logger(verbose = 0):

    root_log = logging.getLogger()
    root_log.setLevel(logging.INFO)
    if verbose:
        root_log.setLevel(logging.DEBUG)

    appname = os.path.basename(sys.argv[0])
    format_str = appname + ': '
    if verbose:
        if verbose > 1:
            format_str += '%(name)s(%(lineno)d) %(funcName)s() '
        else:
            format_str += '%(name)s '
    format_str += '%(levelname)s - %(message)s'
    formatter = ColoredFormatter(format_str)

    # create log handler for console output
    lh_console = logging.StreamHandler(sys.stderr)
    if verbose:
        lh_console.setLevel(logging.DEBUG)
    else:
        lh_console.setLevel(logging.INFO)
    lh_console.setFormatter(formatter)

    root_log.addHandler(lh_console)

    LOG.debug("You are using Python: {0}.{1}.{2}-{3}-{4}.".format(*sys.version_info))


#==============================================================================
class NamedConfParseTestcase(unittest.TestCase):

    #--------------------------------------------------------------------------
    def __init__(self, methodName = 'runTest', verbose = 0):

        self._verbose = int(verbose)

        appname = os.path.basename(sys.argv[0]).replace('.py', '')
        self._appname = appname

        super(NamedConfParseTestcase, self).__init__(methodName)

    # -------------------------------------------------------------------------
    @property
    def appname(self):
        """The name of the current running application."""
        return self._appname

    #--------------------------------------------------------------------------
    @property
    def verbose(self):
        """The verbosity level."""
        return getattr(self, '_verbose', 0)

    #--------------------------------------------------------------------------
    def setUp(self):

        pass

    #--------------------------------------------------------------------------
    def tearDown(self):

        pass

#==============================================================================

if __name__ == '__main__':

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
