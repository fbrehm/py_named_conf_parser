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
from named_conf import default_bind_dir

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
class NamedConfToken(PbBaseObject):
    """
    Encapsulation object of a single token found in a named.conf.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
            value,
            filename,
            row_num,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
            ):
        """
        Initialisation.

        @param value: the read value of the token
        @type value: str
        @param filename: the filename, where this token was found.
        @type filename: str
        @param row_num: the line number in the file, where this token was found.
        @type row_num: int

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

        super(NamedConfToken, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
        )

        self._value = value
        self._filename = filename
        self._row_num = int(row_num)

        self.initialized = True

    #------------------------------------------------------------
    @property
    def value(self):
        """The read value of the token."""
        return self._value

    #------------------------------------------------------------
    @property
    def filename(self):
        """The filename, where this token was found."""
        return self._filename

    #------------------------------------------------------------
    @property
    def row_num(self):
        """The line number in the file, where this token was found."""
        return self._row_num

    #--------------------------------------------------------------------------
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(NamedConfToken, self).as_dict(short = short)

        res['filename'] = self.filename
        res['value'] = self.value
        res['row_num'] = self.row_num

        return res

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
        self._token_list = []

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
    def cur_fobject(self):
        """The file object of the currently opened file."""

        if not self.cur_file:
            return None

        files = getattr(self, '_files', None)
        if not files:
            return None

        if not self.cur_file in files:
            return None
        return files[self.cur_file]['fobject']

    #------------------------------------------------------------
    @property
    def cur_rownum(self):
        """The current row number of the currently opened file."""

        if not self.cur_file:
            return None

        files = getattr(self, '_files', None)
        if not files:
            return None

        if not self.cur_file in files:
            return None
        return files[self.cur_file]['current_rownum']

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
        res['cur_fobject'] = self.cur_file
        res['cur_rownum'] = self.cur_file
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

        fobject = None
        current_filename = filename

        if filename == '-':
            fobject = sys.stdin
            current_filename = '-'
        else:
            fobject = self._open_file(filename)
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
                'fobject': fobject,
                'current_rownum': 0,
                'next_rownum': 1,
            },
        }
        self._in_quoting = False
        self._cur_file_chain = [current_filename]

        ncfg = self.named_conf
        try:
            log.debug("Blubber blub ...")
            bind_dir = self._get_bind_dir()
        finally:
            for cfg_file in self._files.keys():
                if self._files[cfg_file]['fobject'] is not None:
                    log.debug(_("Closing %r ..."), cfg_file)
                    self._files[cfg_file]['fobject'].close()
                    self._files[cfg_file]['fobject'] = None
            self._in_quoting = False
            self._files = {}
            ncfg = self.named_conf
            self.named_conf = None
            self._cur_file_chain = []

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

    #--------------------------------------------------------------------------
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

    #--------------------------------------------------------------------------
    def _get_bind_dir(self):
        """
        Method to get the 'directory' option in the 'options' block.
        This is done without performing includes.

        @return: the 'directory' option in the 'options' block or the default
                 directory option (var/bind)
        @rtype: str
        """

        entry_list = []
        cur_token_list = []

        bind_dir = None

        next_token = self._get_next_token()
        while next_token:
            if self.verbose > 2:
                log.debug(_("Got a token: %s"), next_token)
            cur_token_list.append(next_token)
            next_token = self._get_next_token()

        if not bind_dir:
            bind_dir = default_bind_dir
        return bind_dir

    #--------------------------------------------------------------------------
    def _get_next_token(self):
        """
        Gives the next token from inputstream back.
        Returns None if EOF.

        @return: the next token as an object.
        @rtype: NamedConfToken or None

        """

        if self.verbose > 2:
            log.debug(_("Trying to get the next token ..."))

        # current token list is empty - read the next line
        if not self._token_list:
            next_line = self._read_next_line()
            if self.verbose > 2:
                log.debug(_("Got the next line %r."), next_line)
            if not next_line:
                return None
            while not next_line:
                next_line = self._read_next_line()
                if self.verbose > 2:
                    log.debug(_("Got the next line %r."), next_line)
                if not next_line:
                    return None
            self._token_list = next_line

        # shift from self._token_list and return
        token = self._token_list.pop(0)
        token_obj = NamedConfToken(
                value = token,
                filename = self.cur_file,
                row_num = self.cur_rownum,
                appname = self.appname,
                verbose = self.verbose,
                base_dir = self.base_dir,
                use_stderr = self.use_stderr
        )
        return token_obj

    #--------------------------------------------------------------------------
    def _read_next_line(self):
        """
        Read the next line from current file object.
        Comments are removed.
        The number of the beginning of line can be found after reading in
        self._files[self.cur_file]['current_rownum'] (except in case of EOF).

        @return: the content of this line as a list of tokens or None if EOF
        @rtype: list of str or None

        """

        fobject = self.cur_fobject
        if fobject is None:
            msg = _("Uups. Current file object not found. F***.")
            raise NamedConfParserError(msg)

        cur_rownum = self.cur_rownum + 1
        next_rownum = self.cur_rownum + 1

        if self.verbose > 2:
            log.debug(_("Trying to read the next line from %(file)r (%(nr)d)...") % {
                    'nr': next_rownum, 'file': self.cur_file})

        line = fobject.readline()

        # EOF reached
        if line == '' or line is None:
            if self.verbose > 3:
                log.debug(_("EOF of %r reached."), self.cur_file)
            return None

        if self.verbose > 2:
            log.debug(_("read line %(nr)d: %(line)r") % {
                    'nr': cur_rownum, 'line': line})

        res_array = []

        in_comment = False
        while line:

            line = line.lstrip()

            if self.verbose > 3:
                log.debug(_("Rest of line: %r"), line)

            # Remove C++-like comments
            match = re.search(r'^[^"]*?//', line)
            if match:
                if self.verbose > 3:
                    log.debug(_("Removing C++-like comments in %(file)r line %(nr)d.") % {
                            'nr': next_rownum, 'file': self.cur_file})
                line = re.sub(r'^([^"]*?)//.*\s*', r'\1', line)
                line += "\n"
                continue

            # Remove Perl-like comments
            match = re.search(r'^[^"]*?#', line)
            if match:
                if self.verbose > 3:
                    log.debug(_("Removing Perl-like comments in %(file)r line %(nr)d.") % {
                            'nr': next_rownum, 'file': self.cur_file})
                line = re.sub(r'^([^"]*?)#.*\s*', r'\1', line)
                line += "\n"
                continue

            # Remove C-like comments
            match = re.search(r'^[^"]*?/\*', line)
            if match:

                if self.verbose > 3:
                    log.debug(_("Start of C-like comment detected in %(file)r line %(nr)d.") % {
                            'nr': next_rownum, 'file': self.cur_file})
                line = re.sub(r'^([^"]*?)/\*[^\*]*', r'\1', line)

                do_comment_loop = True
                while do_comment_loop:
                    c_comment_end_match = re.search(r'\*/', line, re.DOTALL)
                    if c_comment_end_match:
                        if self.verbose > 3:
                            log.debug(_("End of C-like comment detected in %(file)r line %(nr)d.") % {
                                    'nr': next_rownum, 'file': self.cur_file})
                        if self.verbose > 3:
                            log.debug(_("Current line before re.sub(): %r"), line)
                        #line = re.sub(r'\n', '', line)
                        line = re.sub(r'.*\*/', '', line, 0, re.DOTALL + re.MULTILINE)
                        if self.verbose > 3:
                            log.debug(_("Current line after re.sub(): %r"), line)
                        do_comment_loop = False
                        break
                    else:
                        new_line = fobject.readline()
                        if new_line == '' or new_line is None:
                            msg = _("Unbalanced C-like comment in %(file)r, starting at line %(line)d.") % {
                                    'file': self.cur_file, 'line': cur_rownum}
                            raise NamedConfParserError(msg)
                        next_rownum += 1
                        if self.verbose > 3:
                            log.debug(_("read line %(nr)d: %(line)r") % {
                                    'nr': next_rownum, 'line': line})
                        line += new_line
                        if self.verbose > 4:
                            log.debug(_("Current line: %r"), line)
                continue

            # Tokens without quotings
            match = re.search(r'^([^"\s]+)', line)
            if match:

                token = match.group(1)
                if self.verbose > 3:
                    log.debug(_("Found token %(t)r in %(file)r line %(nr)d.") % {
                            't': token, 'nr': next_rownum, 'file': next_rownum})

                # Split token by ';' or '{' or '}'
                if token == ';' or token == '{' or token == '}':
                    res_array.append(token)
                else:
                    while token:
                        specialchar_match = re.search(r'^([^;{}]*)([;{}])', token)
                        if specialchar_match:
                            first = specialchar_match.group(1)
                            specialchar = specialchar_match.group(2)
                            if first is not None and first != '':
                                res_array.append(first)
                            res_array.append(specialchar)
                            token = re.sub(r'^[^;{}]*[;{}]', '', token)
                        else:
                            res_array.append(token)
                            token = ''

                line = re.sub(r'^[^"\s]+\s*', '', line)
                continue

            # quoted tokens
            match = re.search( r'^\s*"((?:[^"]|(?<=\\"))*)"', line )
            if match is not None:
                if self.verbose > 3:
                    log.debug(_("Found quoted token %(t)r in %(file)r line %(nr)d.") % {
                            't': match.group(1), 'nr': next_rownum, 'file': next_rownum})
                res_array.append(match.group(1))
                line = re.sub(r'^\s*"(?:[^"]|(?<=\\"))*\s*"', '', line)
                continue

            # tokens with line breaks
            match = re.search(r'^\s*"', line)
            if match:

                token = re.sub(r'^\s*"', '', line)
                if self.verbose > 3:
                    log.debug(_("Found start of quoted token %(t)r in %(file)r line %(nr)d.") % {
                            't': token, 'nr': next_rownum, 'file': next_rownum})

                do_quote_loop = True
                while do_quote_loop:

                    new_line = fobject.readline()

                    if new_line == '' or new_line is None:
                        msg = _("Unbalanced quotings in %(file)r, starting at line %(line)d.") % {
                                'file': self.cur_file, 'line': cur_rownum}
                        raise NamedConfParserError(msg)

                    if self.verbose > 3:
                        log.debug(_("read line %(nr)d: %(line)r") % {
                                'nr': next_rownum, 'line': new_line})
                    next_rownum += 1

                    quote_end_match = re.search(r'((?:[^"]|(?<=\\"))*)"', new_line)
                    if quote_end_match:
                        token += quote_end_match.group(1)
                        res_array.append(token)
                        do_quote_loop = False
                        line = re.sub(r'(?:[^"]|(?<=\\"))*"', '', new_line)
                    else:
                        token += new_line

                continue

            if not res_array:
                if self.verbose > 3:
                    log.debug(_("Currently no valid token fond ..."))
                new_line = fobject.readline()
                if new_line == '' or new_line is None:
                    if self.verbose > 2:
                        msg = _("EOF in %(file)r at line %(line)d reached.") % {
                                'file': self.cur_file, 'line': next_rownum}
                        log.debug(msg)
                    return res_array
                next_rownum += 1
                if self.verbose > 3:
                    log.debug(_("read line %(nr)d: %(line)r") % {
                            'nr': next_rownum, 'line': line})
                line += new_line
                continue

            line = line.lstrip()
            if line == '':
                break

            msg = _("This should not happen! file: %(file)r, line %(nr)d, rest of line: %(rest)r.") % {
                    'file': self.cur_file, 'nr': cur_rownum, 'rest': line}
            raise NamedConfParserError(msg)

        self._files[self.cur_file]['current_rownum'] = next_rownum
        self._files[self.cur_file]['next_rownum'] = next_rownum

        return res_array

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
