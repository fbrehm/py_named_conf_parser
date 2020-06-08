#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2020 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on named.conf parser object
'''

import os
import sys
import logging

try:
    import unittest2 as unittest
except ImportError:
    import unittest

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(0, libdir)

from general import NamedConfParseTestcase, get_arg_verbose, init_root_logger

from fb_tools.common import pp, to_bool

LOG = logging.getLogger('test_parser')

#==============================================================================

class TestNamedConfParser(NamedConfParseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def tearDown(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        LOG.info("Testing import of named_conf ...")
        import named_conf                                           # noqa

        if self.verbose:
            LOG.debug("Version of Module named_conf: {!r}".format(named_conf.__version__))
            LOG.debug("Default named.conf: {!r}".format(named_conf.DEFAULT_NAMED_CONF))
            LOG.debug("Default Bind directory: {!r}".format(named_conf.DEFAULT_BIND_DIR))

#    #--------------------------------------------------------------------------
#    def test_parser_object(self):
#
#        log.info("Testing init of a parser object.")
#
#        cur_dir = os.path.dirname(sys.argv[0])
#        curdir_real = os.path.realpath(cur_dir)
#
#        log.debug("Testing init object without any arguments ...")
#        parser = NamedConfParser(verbose = self.verbose)
#        if self.verbose > 2:
#            log.debug("Parser object:\n%s", parser)
#        self.assertEqual(parser.chroot, None)
#
#        log.debug("Testing init object with the test directory as a chroot dir.")
#        parser = NamedConfParser(chroot = cur_dir, verbose = self.verbose)
#        if self.verbose > 2:
#            log.debug("Parser object:\n%s", parser)
#        self.assertEqual(parser.chroot, curdir_real)
#
#    #--------------------------------------------------------------------------
#    def test_parsing_simple(self):
#
#        log.info("Testing parsing of a simple named.conf ...")
#
#        cur_dir = os.path.dirname(sys.argv[0])
#        curdir_real = os.path.realpath(cur_dir)
#        chroot = os.path.join(curdir_real, 'single')
#
#        parser = NamedConfParser(chroot = chroot, verbose = self.verbose)
#        if self.verbose > 2:
#            log.debug("Parser object:\n%s", parser)
#
#        named_conf = parser()
#        if self.verbose > 2:
#            log.debug("NamedConf object:\n%s", pp(
#                    named_conf.as_dict(short = True)))
#        self.assertIsInstance(named_conf, NamedConf)
#
#    #--------------------------------------------------------------------------
#    def test_named_conf_entry(self):
#
#        log.info("Testing creating and manipulating a NamedConfEntry.")
#
#        entry = NamedConfEntry(verbose = self.verbose)
#        if self.verbose > 2:
#            log.debug("NamedConfEntry object:\n%s", pp(entry.as_dict(short = True)))
#
#        entry.append('Hallo')
#        entry.append(33)
#        entry.append('bunnies')
#        if self.verbose > 2:
#            log.debug("NamedConfEntry object:\n%s", pp(entry.as_dict(short = True)))
#        log.debug("NamedConfEntry typecast into str: %r", str(entry))
#        self.assertEqual(str(entry), 'Hallo 33 bunnies;')
#        log.debug("NamedConfEntry repr: %r", entry)
#
#        #entry.indent = 1
#        #log.debug("NamedConfEntry typecast into str with indention: %r", str(entry))
#        #self.assertEqual(str(entry), '    Hallo 33 bunnies;')
#
#    #--------------------------------------------------------------------------
#    def test_named_conf_block(self):
#
#        log.info("Testing creating and manipulating a NamedConfBlock.")
#
#        block = NamedConfBlock(verbose = self.verbose)
#        if self.verbose > 2:
#            log.debug("NamedConfBlock object:\n%s", pp(block.as_dict(short = True)))
#        log.debug("NamedConfBlock typecast into str: %r", str(block))
#        self.assertEqual(str(block), '{ }')
#
#        block.append(NamedConfEntry('10.1.1.1', verbose = self.verbose))
#        block.append(NamedConfEntry('private_ips', verbose = self.verbose))
#
#        if self.verbose > 2:
#            log.debug("NamedConfBlock object:\n%s", pp(block.as_dict(short = True)))
#        log.debug("NamedConfBlock typecast into str: %r", str(block))
#        self.assertEqual(str(block), '{\n    10.1.1.1;\n    private_ips;\n}')
#        log.debug("NamedConfBlock repr: %r", block)
#
#        block.indent = 2
#        log.debug("NamedConfBlock typecast into str with indention: %r", str(block))
#        self.assertEqual(str(block), '{\n            10.1.1.1;\n            private_ips;\n        }')

#==============================================================================


if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestNamedConfParser('test_import', verbose))
    # suite.addTest(TestNamedConfParser('test_parser_object', verbose))
    # suite.addTest(TestNamedConfParser('test_parsing_simple', verbose))
    # suite.addTest(TestNamedConfParser('test_named_conf_entry', verbose))
    # suite.addTest(TestNamedConfParser('test_named_conf_block', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
