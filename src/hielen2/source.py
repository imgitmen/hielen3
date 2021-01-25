#!/usr/bin/env python
# coding=utf-8
import os
from inspect import ismodule
from abc import ABC, abstractmethod
from importlib import import_module
from hielen2 import db, conf
from hielen2.utils import getSchemaDict
from marshmallow import Schema, fields

def loadModule(proto):
    if ismodule(proto):
        return proto
    mod=db["features_proto"][proto]["module"]
    return import_module(mod)


def moduleActions(proto):
    mod=loadModule(proto)
    return [ k.replace('Schema','').lower() for k in mod.__dict__.keys() if 'Schema' in k ]


def getActionSchema(proto, action):
    mod=loadModule(proto)
    return getSchemaDict(mod.__getattribute__(f"{action.capitalize()}Schema")())


def sourceFactory(featdict,filecache):
    mod = loadModule(featdict['type'])
    return mod.Source(feature=featdict, filecache=filecache)

class ActionSchema(Schema):
    '''
    Minimal ActionSchema object. Used to define at least a timestamp
    '''
    timestamp = fields.DateTime(required=True, allow_none=False)

class HielenSource(ABC):
    def __init__(self, feature, filecache):
        self.__dict__.update(feature)
        self.module = import_module(self.__module__)
        #TODO possibili problemi di sicurezza
        self.filecache = os.path.join(filecache,self.uid)

    def makeCachePath(self,path):
        outpath=os.path.join(self.filecache, path)
        os.makedirs(outpath, exist_ok=True)
        return outpath

    def getRelativePath(self,path):
        return path.replace(f"{self.filecache}/","")

    def execAction(self,action,**kwargs):
        return self.__getattribute__(action)(**kwargs)

    def getActionSchema(self,action):
        return getActionSchema(self.module,action)

    def getActionValues(self,action=None,timestamp=None):
        if action is None:
            action=slice(None,None)
        if timestamp is None:
            timestamp=slice(None,None)
        try:
            return db['actions'][self.uid,action,timestamp]
        except KeyError:
            return []

    def deleteActionValues(self, action, timestamp):
        out=db['actions'][self.uid,action,timestamp]
        
        try:
            f"{action.capitalize()}Schema"
            self.__getattribute__(f"delete{action.capitalize()}")(timestamp)
        except Exception as e:
            pass
        
        try:
            db['actions'][self.uid,action,timestamp]=None
        except Exception as e:
            raise ValueError(e)

        return out


    @abstractmethod
    def data(timefrom=None, timeto=None, geom=None, **kwargs):
        pass
