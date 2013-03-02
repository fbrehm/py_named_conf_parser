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

from named_conf import CommonNamedConfError
from named_conf import default_named_conf

from named_conf.conf import NamedConf

__version__ = '0.3.0'

log = logging.getLogger(__name__)

#---------------------------------------------
# Some module variables

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

        self._chroot = None
        """
        @ivar: a directory used to to read and write all operations
               in a kind of chroot environment
        @type: str or None
        """

        if chroot:
            if not os.path.exists(chroot):
                msg = _("Chroot directory %r doesn't exists.") % (chroot)
                raise NamedConfParserError(msg)
            if not os.path.isdir(chroot):
                msg = _("Given chroot directory %r is not a directory.") % (
                        chroot)
                raise NamedConfParserError(msg)
            self._chroot = os.path.realpath(chroot)

        self._cur_file_chain = []
        """
        @ivar: a list of all currently included files in the order
               of including them, started with the initial named.conf
        @type: list of str
        """

        self._files = {}
        self._in_quoting = False
        self.named_conf = None

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

    #------------------------------------------------------------
    @property
    def in_quoting(self):
        """Is the parser currently in a quoted block."""
        return self._in_quoting

    @in_quoting.setter
    def in_quoting(self, value):
        self._in_quoting = bool(value)

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
        res['in_quoting'] = self.in_quoting

        return res

    #--------------------------------------------------------------------------
    def __call__(self, filename = None):
        """
        Convinience method to call parse().
        """

        if filename is None:
            filename = default_named_conf

        return self.parse(filename)

    #--------------------------------------------------------------------------
    def parse(self, filename = None):
        """
        Read the given file as a named.conf from BIND.

        @raise NamedConfParserError: on an error parsing the file.

        @param filename: filename of the configuration file
                         or '-' or None for standard input.
                         Defaults to /etc/bind/named.conf, if not given.
        @type filename: str

        @return: the parsed named.conf as an object
        @rtype: NamedConf

        """

        if filename is None:
            filename = default_named_conf

        fd = None
        current_filename = filename

        if filename == '-':
            fd = sys.stdin
            current_filename = '-'
        else:
            fd = self._open_file(filename)
            current_filename = self._realpath(filename)

        log.debug(_("Parsing %r ..."), current_filename)

        self.named_conf = NamedConf(
                filename = self._abspath_chroot(filename),
                chroot = self.chroot,
                appname = self.appname,
                verbose = self.verbose,
                base_dir = self.base_dir,
                use_stderr = self.use_stderr,
        )

        self._files = {
            current_filename: {
                'fd': fd,
                'current_rownum': 0,
                'next_rownum': 1,
            },
        }
        self._in_quoting = False

        ncfg = self.named_conf
        try:
            log.debug("Blubber blub ...")
        finally:
            for cfg_file in self._files.keys():
                if self._files[cfg_file]['fd'] is not None:
                    log.debug(_("Closing %r ..."), cfg_file)
                    self._files[cfg_file]['fd'].close()
                    self._files[cfg_file]['fd'] = None
            self._in_quoting = False
            self._files = {}
            ncfg = self.named_conf
            self.named_conf = None

        return ncfg

    #--------------------------------------------------------------------------
    def _abspath(self, path):

        result = None

        if self.chroot:
            npath = os.path.relpath(path, os.sep)
            result = os.path.abspath(os.path.join(self.chroot, npath))
        else:
            result = os.path.abspath(path)

        return result

    #--------------------------------------------------------------------------
    def _realpath(self, path):

        return os.path.realpath(self._abspath(path))

    #--------------------------------------------------------------------------
    def _abspath_chroot(self, path):

        if os.path.isabs(path):
            return os.path.abspath(path)

        apath = os.path.abspath(path)
        if not self.chroot:
            return apath

        npath = os.path.relpath(apath, self.chroot)
        return os.path.abspath(os.path.join(os.sep, npath))

    #------------------------------------------------------
    def _open_file(self, filename):
        """
        Checks the availablity of the given filename, and opens it readonly.

        @raise NamedConfParserError: if the file isn't available, or
                                    another exception if the open fails.

        @param filename: the filename to open
        @type filename: str

        @return: The file object of the opened file
        @rtype: file object

        """

        rname = self._realpath(filename)

        if self.verbose > 2:
            msg = _("Checking %(fname)r (%(rname)s) for open() ...") % {
                    'fname': filename, 'rname': rname}

        if not os.path.isfile(rname):
            msg = _("File %r not found.") % (rname)
            raise NamedConfParserError(msg)

        if not os.access(rname, os.R_OK):
            msg = _("File %r s not readable.") % (rname)
            raise NamedConfParserError(msg)

        if self.verbose > 1:
            log.debug(_("Opening %r ..."), rname)
        return open(rname, "r")

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
