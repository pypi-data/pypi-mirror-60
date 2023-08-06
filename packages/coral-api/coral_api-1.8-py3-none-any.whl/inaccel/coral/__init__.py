# coding: utf-8
"""Inaccel Coral Python API
"""

from __future__ import absolute_import

import os as _os

from ._coral import submit, wait
from ._request import request
from ._numpy_array import array, ndarray

__VERSION_FILE__ = _os.path.join(_os.path.dirname(__file__), 'VERSION')
with open(__VERSION_FILE__) as _f:
    __version__ = _f.read().strip()

__all__ = ['submit', 'wait',
           'request',
           'array', 'ndarray',]
