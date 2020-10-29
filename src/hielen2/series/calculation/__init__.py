#!/usr/bin/env python
# coding=utf-8
__name__ = 'hielen2.series2.calculation'
__version__ = '0.0.1'
__author__ = 'Alessandro Modesti'
__email__ = 'it@img-srl.com'
__description__ = 'hub for hielen calculations'
__license__ = 'MIT'
__uri__ = ''

from pandas import DataFrame, Series
import math
import numpy as np

#### CUSTOM LIBRARY ####
def poly_trans(S0,**kwargs):

    def _parse(k,w):
        k=k.replace('E','')
        return f'{w}*S0**{k}'


    operator='+'.join( _parse(*x) for x in kwargs.items() if x[0][0] in ['E','e'])

    return eval(operator)

def slope(S0,unit,radius):
    if unit=='°' :
        S0=S0[0].apply(lambda x: math.sin(math.radians(x)))
    return S0*radius
    

def aligned(func):

    def wrap_align(left,right):
        left=left.copy()
        right=right.copy()
        try:
            left.columns=list(range(len(left.columns)))
        except AttributeError:
            left.name=0
        try:
            right.columns=list(range(len(right.columns)))
        except AttributeError:
            right.name=0

        left,right = left.align(right,axis=0,copy=False)

        mask = left.notna()[0]

        right = right.fillna(method='pad')
        return func(left[mask],right[mask])

    return wrap_align


@aligned
def add(left,right):
    right = right.fillna(0)
    return left+right


@aligned
def sub(left,right):
    right = right.fillna(0)
    return left-right

def filter(b):
    d=abs(b-b.rolling(window=50,center=True,min_periods=1).apply(np.mean))
    std=abs(b.rolling(window=50,center=True,min_periods=1).apply(np.std))
    return b[d < 3*std]


def int_or_str(value):
    try:
        return int(value)
    except ValueError:
        return value

VERSION = tuple(map(int_or_str, __version__.split('.')))

__all__ = ['poly_trans','add','sub','slope']
