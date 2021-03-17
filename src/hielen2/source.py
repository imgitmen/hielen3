#!/usr/bin/env python
# coding=utf-8
import os, re
from glob import glob
from pathlib import Path, os
from inspect import ismodule
from abc import ABC, abstractmethod
from importlib import import_module
from hielen2 import db, conf
from hielen2.utils import getSchemaDict
from marshmallow import Schema, fields, ValidationError
from numpy import datetime64

def loadModule(proto):
    if ismodule(proto):
        return proto

    mod=db["features_proto"][proto]["module"]
    try:
        return import_module(mod)
    except Exception as e:
        raise e
        return proto

def moduleActions(proto):
    mod=loadModule(proto)
    try:
        return [ k.replace('Schema','').lower() for k in mod.__dict__.keys() if 'Schema' in k ]
    except Exception as e:
        return []

def getActionSchemaClass(proto, action):
    mod=loadModule(proto)
    return mod.__getattribute__(f"{action.capitalize()}Schema")

def getActionSchema(proto, action):
    return getSchemaDict(getActionSchemaClass(proto, action)())

def sourceFactory(feat):
    if isinstance(feat, str):
        feat=db['features'][feat]
    return loadModule(feat['type']).Source(feature=feat)


class SourceCache():

    def __init__(self, syspath, subpath=''):
        self.cache=Path(syspath) / subpath

    def __truediv__(self, other):
        other = str(other).replace(f"{self.cache}{os.sep}","")
        return self.cache / other

    def mkdir(self,path=''):
        outpath = self / path
        os.makedirs( outpath , exist_ok=True)
        return outpath

    def hasher(self,*args,**kwargs):
        h=[ *args ]
        h.extend(list(kwargs.values()))
        h=''.join([ str(a) for a in h])
        return re.sub("[^\d]","",h)  

def _agoodtime(t):

    try:
        t=np.datetime64(t)
        assert not np.isnat(t)
        t=str(t)
    except Exception:
        t=None
    return t


class StringTime(fields.DateTime):

    def _deserialize(self, value, attr, data, **kwargs):
        return str(super()._deserialize(value, attr, data, **kwargs))

    def _serialize(self, value, attr, obj, **kwargs):
        return _agoodtime(value)

class ActionSchema(Schema):
    '''
    Minimal ActionSchema object. Used to define at least a timestamp
    '''
    timestamp = StringTime(required=True, allow_none=False)

class HielenSource(ABC):
    def __init__(self, feature):
        self.__dict__.update(feature)
        self.module = import_module(self.__module__)
        #TODO possibili problemi di sicurezza
        for k,w in conf['syscache'].items():
            self.__setattr__(k, SourceCache(w,self.uid) )

    def execAction(self,action,**kwargs):
        aclass=getActionSchemaClass(self.module,action)
        try:
            kwargs=aclass().load(kwargs)
            return self.__getattribute__(action)(**kwargs)
        except Exception as e:
            raise ValueError(e)


    def getActionSchema(self,action):
        return getActionSchema(self.module,action)

    def getActionValues(self,action=None,timestamp=None):
        if action is None:
            action=slice(None,None)
        if timestamp is None:
            timestamp=slice(None,None)
        try:
            out = db['actions'][self.uid,action,timestamp]
            if not isinstance(out,list):
                out = [out]
        except KeyError:
            return []

        return out

    def deleteActionValues(self, action=None, timestamp=None):
        out=self.getActionValues(action,timestamp)

        if not isinstance(out,list):
            out=[out]

        for act in out:

            a=act['action']
            t=act['timestamp']
        
            try:
                f"{a.capitalize()}Schema"
                self.__getattribute__(f"clean{a.capitalize()}")(t)
            except Exception as e:
                pass
            
            try:
                db['actions'][self.uid,a,t]=None
            except Exception as e:
                raise ValueError(e)

        return out


    @abstractmethod
    def data(timefrom=None, timeto=None, geom=None, **kwargs):
        pass
