#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame,Series
from time import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from numpy import nan, unique
from importlib import import_module
from hielen2 import db
from hielen2.utils import isot2ut, ut2isot


def _threadpool(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        return ThreadPoolExecutor().submit(f, *args, **kwargs)

    return wrap


class Series:
    def __init__(self, uid):
        series_info = db["series"][uid]

        self.__dict__.update(series_info)
        geninfo = dict(
            (k, w)
            for k, w in series_info.items()
            if k in ("modules", "operator", "operands")
        )
        self.generator = Generator(**geninfo)

    @_threadpool
    def thdata(self, times=None, timeref=None, refresh=None, *args, **kwargs):
        return self.data(times, timeref, refresh)

    def data(self, times=None, timeref=None, refresh=None, *args, **kwargs):

        try:
            
            if refresh is not None and refresh:
                raise KeyError

            out = db["datacache"][self.uid][times]

        except KeyError:
            out = self.generator._generate(times, timeref=timeref,**kwargs)
            try:
                out = out[out.columns[0]]
            except AttributeError:
                pass

            try:
                db["datacache"].update(self.uid,out)
            except KeyError as e:
                db["datacache"][self.uid]=out

        out.index.name = "timestamp"

        return out


class Generator:
    def __init__(self, modules=None, operator=None, operands=None):

        self.operator = operator or "mod.map(**operands)"
        self.modules = {}

        if not modules is None:
            for k, m in modules.items():
                self.operator = self.operator.replace(k, f"self.modules[{k!r}]")
                self.modules[k] = import_module(m)

        self.operands = {}
        if operands is not None:
            self.operands = dict(
                Generator._parse_operand(*op) for op in operands.items()
            )

    def _parse_operand(key, value):

        """
        trying to extract a series
        """
        try:
            return (key, Series(value))
        except KeyError:
            pass


        """
            trying to extract element attribute
        """

        #TODO modificare per utilizare configurazione
        try:
            v = value.split(".")
            assert v.__len__() == 2
            return (key, db["features"][v[0]]["properties"][v[1]])
        except Exception:
            pass

        """
            giving up. It should be a scalar.
            return it
        """

        return (key, value)

    def _generate(self, times, timeref, **kwargs):

        operands = dict(times=times, timeref=timeref, **kwargs)
        operands.update(
            {k: w for k, w in self.operands.items() if not isinstance(w, Series)}
        )

        runners = {
            k: w.thdata(times, timeref)
            for k, w in self.operands.items()
            if isinstance(w, Series)
        }

        operands.update({k: w.result() for k, w in runners.items()})
        #operands.update( { k:w.data(times, timeref, **kwargs) for k,w in self.operands.items() if isinstance(w,Series) } )

        #print('OPERANDI',operands)
        #print('OPERATORE', self.operator)

        return eval(self.operator)
