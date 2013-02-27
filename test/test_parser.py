#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2013 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on named.conf parser object
'''

import unittest
import os
import sys
import logging

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'src'))
sys.path.insert(0, libdir)

import general
from general import NamedConfParseTestcase, get_arg_verbose, init_root_logger

import pb_base.object
from pb_base.object import PbBaseObjectError

from pb_base.common import pp

import named_conf
from named_conf import CommonNamedConfError

import named_conf.parser
from named_conf.parser import NamedConfParserError
from named_conf.parser import NamedConf
from named_conf.parser import NamedConfParser

log = logging.getLogger(__name__)

#==============================================================================

class TestNamedConfParser(NamedConfParseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_parser_object(self):

        log.info("Testing init of a parser object.")

        cur_dir = os.path.dirname(sys.argv[0])
        curdir_real = os.path.realpath(cur_dir)

        log.debug("Testing init object without any arguments ...")
        parser = NamedConfParser(verbose = self.verbose)
        if self.verbose > 2:
            log.debug("Parser object:\n%s", parser)
        self.assertEqual(parser.chroot, None)

        log.debug("Testing init object with the test directory as a chroot dir.")
        parser = NamedConfParser(chroot = cur_dir, verbose = self.verbose)
        if self.verbose > 2:
            log.debug("Parser object:\n%s", parser)
        self.assertEqual(parser.chroot, curdir_real)

    #--------------------------------------------------------------------------
    def test_parsing_simple(self):

        log.info("Testing parsing of a simple named.conf ...")

        cur_dir = os.path.dirname(sys.argv[0])
        curdir_real = os.path.realpath(cur_dir)
        chroot = os.path.join(curdir_real, 'single')

        parser = NamedConfParser(chroot = chroot, verbose = self.verbose)
        if self.verbose > 2:
            log.debug("Parser object:\n%s", parser)

        named_conf = parser()
        if self.verbose > 2:
            log.debug("NamedConf object:\n%s", pp(
                    named_conf.as_dict(short = True)))
        self.assertIsInstance(named_conf, NamedConf)

#==============================================================================


if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestNamedConfParser('test_parser_object', verbose))
    suite.addTest(TestNamedConfParser('test_parsing_simple', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
