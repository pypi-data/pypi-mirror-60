"""
This module handles dcli default options logic
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2018-2020 VMware, Inc.  All rights reserved.'
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import sys
from collections import OrderedDict

from vmware.vapi.client.dcli.__version__ import (
    __version__, __build__)


class About(object):
    """
    Provides commands for retrieving information about dcli package
    """
    def __init__(self, dcli_context=None):
        pass

    def get(self):  # pylint: disable=W0611,R0201
        """
        Retrieves information about dcli package such as version used

        :rtype: :class:`str`
        :return: common dcli version information.
        """
        result = OrderedDict()
        result["version"] = "{}".format(__version__)
        result["build"] = "{}".format(__build__)
        result["python version"] = "{}".format(sys.version)
        return result
