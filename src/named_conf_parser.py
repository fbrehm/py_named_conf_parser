#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2013 by Profitbricks GmbH
@license: GPL3
@summary: Module for a class parsing a named.conf of BIND
"""

# Standard modules
import sys
import os
import logging
import re
import glob

from gettext import gettext as _

# Third party modules

# Own modules
from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

from pb_base.handler import PbBaseHandlerError
from pb_base.handler import PbBaseHandler

__version__ = '0.1.0'

log = logging.getLogger(__name__)

#---------------------------------------------
# Some module variables

default_named_conf = os.sep + os.path.join('etc', 'bind', 'named.conf')


#==============================================================================
class NamedConfParserError(PbBaseHandlerError):
    """
    Base error class for all exceptions belonging to the named.conf parser
    """

    pass

#==============================================================================
class NamedConfParser(PbBaseHandler):
    """
    Class for a object parsing a named.conf from BIND.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
            chroot = None,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
            simulate = False,
            *targs,
            **kwargs
            ):
        """
        Initialisation of the base blockdevice object.

        @raise CommandNotFoundError: if some needed commands could not be found.
        @raise NamedConfParserError: on a uncoverable error in initialisation.

        @param chroot: a directory used to to read and write all operations
                       in a kind of chroot environment
        @type chroot: str or None
        @param appname: name of the current running application
        @type appname: str
        @param verbose: verbose level
        @type verbose: int
        @param version: the version string of the current object or application
        @type version: str
        @param base_dir: the base directory of all operations
        @type base_dir: str
        @param use_stderr: a flag indicating, that on handle_error() the output
                           should go to STDERR, even if logging has
                           initialized logging handlers.
        @type use_stderr: bool
        @param simulate: don't execute actions, only display them
        @type simulate: bool

        @return: None

        """

        super(NamedConfParser, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
                simulate = simulate,
                sudo = False,
                quiet = False,
        )

        self._chroot = chroot
        """
        @ivar: a directory used to to read and write all operations
               in a kind of chroot environment
        @type: str or None
        """

        self._cur_file_chain = []
        """
        @ivar: a list of all currently included files in the order
               of including them, started with the initial named.conf
        @type: list of str
        """

        self.initialized = True

    #------------------------------------------------------------
    @property
    def chroot(self):
        """A directory used to to read and write all operations
           in a kind of chroot environment."""

        return self._chroot

    #------------------------------------------------------------
    @property
    def cur_file(self):
        """The file, which is currently parsed."""

        if not self._cur_file_chain:
            return None
        return self._cur_file_chain[-1]

    #--------------------------------------------------------------------------
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(NamedConfParser, self).as_dict(short = short)

        res['chroot'] = self.chroot
        res['cur_file'] = self.cur_file

        return res

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
