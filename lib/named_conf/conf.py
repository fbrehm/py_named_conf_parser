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

from named_conf import CommonNamedConfError

__version__ = '0.1.0'

log = logging.getLogger(__name__)

#---------------------------------------------
# Some module variables

#==============================================================================
class NamedConf(PbBaseObject):
    """
    Encapsulation class for a complete parsed named.conf
    """

    #--------------------------------------------------------------------------
    def __init__(self,
            filename,
            chroot = None,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
            ):
        """
        Initialisation of the NamedConf object.

        @param filename: the filename of the named.conf as an absolute path
                         without a possibly chroot directory.
        @type filename: str
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

        """

        super(NamedConf, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
        )

        self._filename = filename
        self._chroot = chroot

        self.initialized = True

    #------------------------------------------------------------
    @property
    def filename(self):
        """The filename of the named.conf as an absolute path without
            a possibly chroot directory."""

        return self._filename

    #------------------------------------------------------------
    @property
    def chroot(self):
        """A directory used to to read and write all operations
           in a kind of chroot environment."""

        return self._chroot

    #--------------------------------------------------------------------------
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(NamedConf, self).as_dict(short = short)

        res['chroot'] = self.chroot
        res['filename'] = self.filename

        return res

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
