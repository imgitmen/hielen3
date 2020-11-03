#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame
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
        

class Series():

    def __init__(self,code):
        series_info=db['series'][code]

        self.__dict__.update(series_info)
        geninfo=dict((k,w) for k,w in series_info.items() if k in ( "modules","operator","operands" ) )
        self.generator = Generator(**geninfo)


    @_threadpool
    def thdata(self,timefrom=None,timeto=None,*args,**kwargs):
        return self.data(timefrom,timeto)


    def data(self,timefrom=None, timeto=None):

        if timefrom is not None:
            if self.first is not None:
                timefrom = max(self.first,timefrom)
        else:
            timefrom = self.first
        
        if timeto is not None:
            if self.last is not None:
                timeto = min(self.last,timeto)
        else:
            timeto = self.last

        try:
            out = db['datacache'][self.code].to_frame()
            if timefrom is not None and out.index.max() < timefrom:
                out = out.tail(1)
            else:
                out = out[timefrom:timeto]
        except KeyError:
            out = DataFrame()

        timefrom2=out.index.max()
        
        if timefrom2 is nan:
            timefrom2 = timefrom
        else:
            #timefrom2 = max(isot2ut(timefrom2),isot2ut(timefrom) or 1)
            timefrom2 = max(isot2ut(timefrom2),isot2ut(timefrom) or 1)
            timefrom2 = ut2isot(timefrom2)


        gen = self.generator._generate(timefrom=timefrom2,timeto=timeto)

        try:
            gen = gen.to_frame()
        except AttributeError:
            pass

        gen.columns=list(range(gen.columns.__len__()))

        out = out.append(gen).sort_index()
        idx= unique( out.index.values, return_index = True )[1]
        out = out.iloc[ idx ]
        out.index.name='timestamp'
        
        return out

class Generator:
    
    def __init__(self,modules=None,operator=None,operands=None):

        self.operator = operator or 'DataFrame()'
        self.modules = {}

        if not modules is None:
            for k,m in modules.items():
                self.operator=self.operator.replace(k,f'self.modules[{k!r}]')
                self.modules[k]=import_module(m)

        self.operands = {}
        if operands is not None:
            self.operands = dict( Generator._parse_operand(*op) for op in operands.items() )


    def _parse_operand(key,value):

        '''
            trying to extract a series
        '''
        try:
            return (key,Series(value))
        except KeyError:
            pass

        '''
            trying to extract element attribute
        '''

        try:
            v=value.split('.')
            assert (v.__len__()==2)
            return (key,db['elements'][v[0]][v[1]])
        except Exception:
            pass

        '''
            giving up. It should be a scalar.
            return it
        '''

        return (key, value)


    def _generate(self,timefrom, timeto):

        operands=dict(timefrom=timefrom,timeto=timeto)
        operands.update( { k:w for k,w in self.operands.items() if not isinstance(w,Series) })

        runners = { k:w.thdata(timefrom,timeto) for k,w in self.operands.items() if isinstance(w,Series) }
        operands.update( { k:w.result() for k,w in runners.items() } )
        #operands.update( { k:w.data(timefrom,timeto) for k,w in self.operands.items() if isinstance(w,Series) } )

        #print('OPERANDI',operands)
        #print('OPERATORE', self.operator)
        return eval(self.operator)

