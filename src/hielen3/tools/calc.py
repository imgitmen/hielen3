#!/usr/bin/env python
# coding=utf-8
__name__ = "hielen3.series.calc"
__version__ = "0.0.1"
__author__ = "Alessandro Modesti"
__email__ = "it@img-srl.com"
__description__ = "hub for hielen calculations"
__license__ = "MIT"
__uri__ = ""

from pandas import Series, Timedelta, DataFrame
from numpy import sin, radians, mean, std, nan

#### CUSTOM LIBRARY ####
def poly_trans(S0, **kwargs):
    def _parse(k, w):
        k = k.replace("E", "").replace("e", "")
        return f"{w}*S0**{k}"

    operator = "+".join(_parse(*x) for x in kwargs.items() if x[0][0] in ["E", "e"])

    return eval(operator)


def poly_trans2(S0, *args):

    if args.__len__() > 0:
        __res__ = args[0]*S0**0
    else:
        return S0

    try:
        for i in range(1, args.__len__()):
            try:
                __res__ += args[i]*S0**i
            except Exception:
                pass
    except Exception:
        pass

    return __res__


def slope(S0, unit="°", radius=1):

    if unit == "°":
        S0 = radians(S0)
        unit = "rad"

    if unit == "rad":
        S0 = sin(S0)

    return S0 * radius


def aligned(func):
    def wrap_align(left, right):
        try:
            left = left.copy()
            right = right.copy()
            try:
                left.columns = list(range(len(left.columns)))
            except AttributeError:
                left.name = 0
            try:
                right.columns = list(range(len(right.columns)))
            except AttributeError:
                right.name = 0

            left, right = left.align(right, axis=0, copy=False)

            mask = left.notna()[0]

            right = right.fillna(method="pad")
            return func(left[mask], right[mask])
        except Exception as e:
            return func(left,right)

    return wrap_align


def reference(s_main,s_ref):

    try:
        t=s_main.index[0]
    except Exception as e:
        t=None

    try:
        s_main,s_ref=s_main.align(s_ref,method='ffill',copy=True)
        s_ref=s_ref.fillna(0)
    except Exception as e:
        pass

    result=(s_main-s_ref)[t:].dropna()

    return result



@aligned
def add(left, right):
    try:
        right = right.fillna(0)
    except Exception as e:
        pass
    return left + right


def sub(left, right):
    return add(left, -1 * right)

@aligned
def mult(left, right):
    try:
        right = right.fillna(0)
    except Exception as e:
        pass

    return left * right


def filter(b,sigma=3,window=50,center=False,min_periods=1):
    d = abs(b - b.rolling(window=window, center=center, min_periods=min_periods).apply(mean))
    stdv = abs(b.rolling(window=window, center=center, min_periods=min_periods).apply(std))
    return b[d < sigma * stdv]


def threshold(S0, limit=0, how='<', action='clean'):
    """
    action: ['clean','drop','signal']
    """

    out=eval(f"S0 {how} {limit}")

    if action == 'signal':
        return out

    if action == 'drop':
        S1 = S0[out].copy()
        return S1

    if action == 'clean':
        S1=S0.copy()
        S1[out] = nan
        return S1
    




def instant_velocity(S0,time_unit_denom='hours'):

    if not isinstance( time_unit_denom, Timedelta ):
        time_unit_denom=Timedelta(f"1 {time_unit_denom}")

    time_unit_denom=time_unit_denom.total_seconds()

    timestoman=Series(S0.index.values,index=S0.index,dtype='datetime64[ns]')
    seconds=(timestoman - timestoman.shift(1)).apply(lambda x: x.total_seconds())


    return (S0/seconds*time_unit_denom).replace(nan,0)

def int_or_str(value):
    try:
        return int(value)
    except ValueError:
        return value


VERSION = tuple(map(int_or_str, __version__.split(".")))

__all__ = ["poly_trans", "add", "sub", "slope","filter","instant_velocity"]



# coding: utf-8


