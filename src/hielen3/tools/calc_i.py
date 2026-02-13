#!/usr/bin/env python
# coding=utf-8
__name__ = "hielen3.series.calc_i"
__version__ = "0.0.1"
__author__ = "Alessandro Modesti"
__email__ = "it@img-srl.com"
__description__ = "hub for hielen calculations"
__license__ = "MIT"
__uri__ = ""

from pandas import Series, Timedelta, DataFrame, concat
from numpy import sin, cos, radians, mean, std, nan, radians as rad

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
    def wrap_align(left, right, *args, **kwargs):
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

            #right = right.fillna(method="pad")
            return func(left[mask], right[mask], *args, **kwargs)
        except Exception as e:
            return func(left,right, *args, **kwargs)

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


def oblivion(S0,mask=None):

    if mask is None: return S0

    return S0[S0.align(mask)[1].isna()]


def clean_frame(df):
    return df[df.notna().all(axis=1)]


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



def rotation(func):
    def wrap_rot(x, y, alpha=None, unit=None, *args, **kwargs):
        if unit is None:
            unit = "°"

        if alpha is None:
            alpha = 0

        if unit == "°":
            alpha = rad(alpha)

        return func(x, y, alpha, unit, *args, **kwargs)

    return wrap_rot




@rotation
@aligned
def rotate_X(x=None,y=None,alpha=None,*args,**kwargs):
    return x*cos(alpha) - y*sin(alpha)

@rotation
@aligned
def rotate_Y(x=None,y=None,alpha=None,*args,**kwargs):
    return x*sin(alpha) + y*cos(alpha)



def hist_merge(H=None,S0=None):
   
    if H is None or H.empty:
        return S0

    if S0 is None or S0.empty:
        return H


    try:
        S0=S0.to_frame()
    except Exception as e:
        pass

    try:
        H=H.to_frame()
    except Exception as e:
        pass

    S0=S0.copy()
    H=H.copy()

    H.columns=range(0,H.columns.__len__())
    S0.columns=H.columns

    S0.index.name='timestamp'
    H.index.name='timestamp'

    last=H.index[-1]

    out=concat([H,S0.loc[last:]])

    out=out[~out.index.duplicated(keep='first')]
    
    return out


def snap_anchor(s,anchor=None):
    if anchor is None:
        return s
    if anchor <= 0:
        return s
    if anchor > len(s):
        return s

    anchor_value=s.iloc[anchor-1]
    step= anchor_value / anchor
    correction=s.copy()
    correction.loc[:]=step
    correction=correction.cumsum()
    s=(s-correction).round(6)
    return s


def chain_integ(s,direction=None,anchor=None):
    if direction is None:
        direction = 1

    if direction < 0:
        s = s.iloc[::-1]

    s=s.cumsum(skipna=False)

    if anchor is not None and direction < 0:
        anchor=len(s)-anchor

    if anchor is not None and anchor > 0 and anchor <= len(s):
        s=snap_anchor(s,anchor)

    if direction < 0:
        s=s.iloc[::-1]

    return s


VERSION = tuple(map(int_or_str, __version__.split(".")))

__all__ = ["poly_trans", "add", "sub", "slope","filter","instant_velocity","rotate_X","rotate_Y","hist_merge","snap_anchor"]



# coding: utf-8


