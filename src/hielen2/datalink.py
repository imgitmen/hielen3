#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame
from abc import ABC,abstractmethod 
from hielen2.utils import loadjsonfile, newinstanceof

def dbinit(conf):
    conf['substs']
    return { k:newinstanceof(w['klass'],w['connection'].format(**conf['substs']))  for k,w in conf['db'].items() }

class DB(ABC):

    @abstractmethod
    def __init__(self,connection):
        pass

    @abstractmethod
    def get(self,key):
        pass

class JsonDB(DB):

    def __init__(self,connection):
        self.db=loadjsonfile(connection)

    def get(self, key=None):

        if isinstance(key,list):
            try:
                key=list(filter(None, key))
            except TypeError:
                pass

        if key is None:
            return self.db

        if not isinstance(key,list):
            try:
                return self.db[key]
            except KeyError:
                return None

        return { k:w for k,w in self.db.items() if k in key }


class JsonCache(DB):

    def __init__(self,connection):
        self.cache=loadjsonfile(connection)

    def get(self,key,timefrom=None,timeto=None):
        out = DataFrame(columns=[0])
        try:
            out = DataFrame(self.cache[key]).set_index(['timestamp']).sort_index()
            if timefrom is not None and out.index.max() < timefrom:
                out = out.tail(1)
            else:
                out = out.loc[timefrom:timeto]
        except Exception:
            pass
 
        return out

