#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2020 by Frank Brehm, Berlin
@summary: A module for the IscConfItem object
"""
from __future__ import absolute_import

import copy

from pathlib import Path

from fb_tools.obj import FbBaseObject
from fb_tools.common import is_sequence

from .. import CommonIscConfError

__version__ = '0.1.0'


# =============================================================================
class IscConfItem(list, FbBaseObject):
    """
    Encapsulation object of a complete configuration entry (all tokens until
    the finishing semicolon.
    """

    default_base_indent = "    "
    default_indent = 0

    # -------------------------------------------------------------------------
    def __init__(self, items=None, indent=None, base_indent=None, appname=None, verbose=0,
            version=__version__, base_dir=None, initialized=False):

        self._items = []
        self._indent = self.default_indent
        self.__base_indent = self.default_base_indent

        super(IscConfItem, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            initialized=False)

        if indent is not None:
            self.indent = indent

        if base_indent is not None:
            self.base_indent = base_indent

        if is_sequence(items):
            for item in items:
                self.append(item)
        elif items is not None:
            self._items.append(items)

        if initialized:
            self.initialized = True


    # -----------------------------------------------------------
    @property
    def indent(self):
        """The indent level of the current entry"""
        return self._indent

    @indent.setter
    def indent(self, value):
        if value is None:
            msg = "Value for indent may not be None"
            raise TypeError(msg)
        self._indent = int(value)

    # -----------------------------------------------------------
    @property
    def base_indent(self):
        """The indent, if the indent level is exactly 1."""
        return self._base_indent

    @base_indent.setter
    def base_indent(self, value):
        if not isinstance(value, str):
            msg = "Value for base_indent must be str (is {!r}).".format(value)
            raise TypeError(msg)
        self._base_indent = value

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict or list
        @rtype:  dict or list
        """

        res = super(IscConfItem, self).as_dict(short=short)
        res['_items'] = copy.copy(self._items)
        res['base_indent'] = self.base_indent
        res['indent'] = self.indent

        return res

    # -------------------------------------------------------------------------
    def index(self, search_item, *args):

        i = None
        j = None

        if len(args) > 0:
            if len(args) > 2:
                msg = "{m} takes at most {max} arguments ({n} given).".format(
                    m='index()', max=3, n=len(args) + 1)
                raise TypeError(msg)
            i = int(args[0])
            if len(args) > 1:
                j = int(args[1])

        index = 0
        start = 0
        if i is not None:
            start = i
            if i < 0:
                start = len(self._items) + i

        wrap = False
        end = len(self._items)
        if j is not None:
            if j < 0:
                end = len(self._items) + j
                if end < index:
                    wrap = True
            else:
                end = j
        for index in list(range(len(self._items))):
            item = self._items[index]
            if index < start:
                continue
            if index >= end and not wrap:
                break
            if item == search_item:
                return index

        if wrap:
            for index in list(range(len(self._items))):
                item = self._items[index]
                if index >= end:
                    break
            if item == search_item:
                return index

        msg = "Item is not in items list."
        raise ValueError(msg)

    # -------------------------------------------------------------------------
    def __contains__(self, search_item):

        if not self._items:
            return False

        for item in self._items:
            if item == search_item:
                return True

        return False

    # -------------------------------------------------------------------------
    def count(self, search_item):

        if not self._items:
            return 0

        num = 0
        for item in self._items:
            if item == search_item:
                num += 1
        return num

    # -------------------------------------------------------------------------
    def __len__(self):
        return len(self._items)

    # -------------------------------------------------------------------------
    def __getitem__(self, key):
        return self._items.__getitem__(key)

    # -------------------------------------------------------------------------
    def __reversed__(self):

        return reversed(self._items)

    # -------------------------------------------------------------------------
    def __setitem__(self, key, item):

        if not isinstance(item, str):
            msg = "An item must be of type str, is {!r}.".format(item)
            raise TypeError(msg)

        self._items.__setitem__(key, item)

    # -------------------------------------------------------------------------
    def __delitem__(self, key):

        del self._items[key]

    # -------------------------------------------------------------------------
    def append(self, item^):

        if not isinstance(item, str):
            msg = "An item must be of type str, is {!r}.".format(item)
            raise TypeError(msg)

        self._items.append(.disk)

    # -------------------------------------------------------------------------
    def insert(self, index, item):

        if not isinstance(item, str):
            msg = "An item must be of type str, is {!r}.".format(item)
            raise TypeError(msg)

        self._items.insert(index, item)

    # -------------------------------------------------------------------------
    def clear(self):

        self._items = []

    # -------------------------------------------------------------------------
    def __str__(self):

        if not len(self):
            return ''

        ind = self.indent
        if ind < 0:
            ind = 0

        out = ''

        i = 0
        for item in self:
            i += 1
            out += str(item)
            if i < len(self):
                out += ' '
        out += ';'

        return out


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4
