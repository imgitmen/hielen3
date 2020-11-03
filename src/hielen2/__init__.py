# coding=utf-8

__name__ = 'hielen2'
__version__ = '2.0.1'
__author__ = 'Alessandro Modesti'
__email__ = 'it@img-srl.com'
__description__ = 'Multidimention Hierarichical Elaboration Engine'
__license__ = 'MIT'
__uri__ = ''

import warnings

from .datalink import dbinit #, cacheinit
from .utils import loadjsonfile


conf=loadjsonfile('./conf/hielen.json')
db=dbinit(conf)

def int_or_str(value):
    try:
        return int(value)
    except ValueError:
        return value

VERSION = tuple(map(int_or_str, __version__.split('.')))

__all__ = ['api','conf', 'db', ]
