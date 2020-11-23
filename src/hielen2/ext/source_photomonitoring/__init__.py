# coding=utf-8

__name__ = 'hielen2.ext.photomonitoring'
__version__ = '0.0.1'
__author__ = 'Alessandro Modesti'
__email__ = 'it@img-srl.com'
__description__ = 'photomonitornig hiele actions manager'
__license__ = 'MIT'
__uri__ = ''


def config(**kwargs):
    return kwargs

def int_or_str(value):
    try:
        return int(value)
    except ValueError:
        return value

VERSION = tuple(map(int_or_str, __version__.split('.')))

__all__ = ['config']
