#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 201r32 by Frank Brehm, Berlin
@summary: All modules used by named_conf package
"""

import os
import sys

# Own modules

from pb_base.object import PbBaseObjectError

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010-2013 ProfitBricks GmbH, Berlin'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.3.0'
__license__ = 'GPL3'

#---------------------------------------------
# Some module variables

default_named_conf = os.sep + os.path.join('etc', 'bind', 'named.conf')
default_bind_dir = os.sep + os.path.join('var', 'bind')

#==============================================================================
class CommonNamedConfError(PbBaseObjectError):
    """
    Base error class for all exceptions belonging to the named_conf package
    """

    pass

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4