#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2020 by Frank Brehm, Berlin
@summary: All modules used by named_conf package
"""
from __future__ import absolute_import

from pathlib import Path

# Own modules
from fb_tools.errors import FbError

__version__ = '0.4.0'

#---------------------------------------------
# Some module variables

DEFAULT_NAMED_CONF = Path('/etc') / 'bind' / 'named.conf'
DEFAULT_BIND_DIR = Path('/var') / 'bind'


#==============================================================================
class CommonIscConfError(FbError):
    """
    Base error class for all exceptions belonging to the named_conf package
    """
    pass


#==============================================================================
class CommonNamedConfError(CommonIscConfError):
    """
    Base error class for all exceptions belonging to the named_conf package
    """
    pass


#==============================================================================

if __name__ == "__main__":

    pass


# vim: fileencoding=utf-8 filetype=python ts=4
