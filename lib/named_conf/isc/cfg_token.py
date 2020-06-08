#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2020 by Frank Brehm, Berlin
@summary: A module for the IscConfToken object
"""
from __future__ import absolute_import

from pathlib import Path

from fb_tools.obj import FbBaseObject

from .. import CommonIscConfError

__version__ = '0.1.1'


# =============================================================================
class IscConfToken(FbBaseObject):
    """Encapsulation object of a single token found in an ISC styled config file."""

    # -------------------------------------------------------------------------
    def __init__(self, value, filename, row_num, appname=None, verbose=0,
            version=__version__, base_dir=None, initialized=False):
        """
        Initialisation.

        @param value: the read value of the token
        @type value: str
        @param filename: the filename, where this token was found.
        @type filename: str
        @param row_num: the line number in the file, where this token was found.
        @type row_num: int

        """

        self._value = value
        self._filename = Path(filename)
        self._row_num = int(row_num)

        super(IscConfToken, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            initialized=False)

        if initialized:
            self.initialized = True

    # -----------------------------------------------------------
    @property
    def value(self):
        """The read value of the token."""
        return self._value

    # -----------------------------------------------------------
    @property
    def filename(self):
        """The filename, where this token was found."""
        return self._filename

    # -----------------------------------------------------------
    @property
    def row_num(self):
        """The line number in the file, where this token was found."""
        return self._row_num

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(IscConfToken, self).as_dict(short=short)
        res['value'] = self.value
        res['filename'] = self.filename
        res['row_num'] = self.row_num

        return res

    #--------------------------------------------------------------------------
    def __repr__(self):
        """Typecasting into a string for reproduction."""

        out = super(IscConfToken, self).__repr__()[:-2]

        fields = []
        fields.append("filename={!r}".format(self.filename))
        fields.append("value={!r}".format(self.value))
        fields.append("row_num={!r}".format(self.row_num))

        if fields:
            out += ', ' + ", ".join(fields)
        out += ")>"
        return out

    #--------------------------------------------------------------------------
    def __str__(self):
        """Typecasting into a string."""

        return "{val!r} ({fn}:{rn})".format(
            val=self.value, fn=self.filename, rn=self.row_num)


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4
