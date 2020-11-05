#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame, read_json
from abc import ABC,abstractmethod 
from hielen2.utils import loadjsonfile, savejsonfile, newinstanceof

def dbinit(conf):
    conf['substs']
    return { k:newinstanceof(w['klass'],w['connection'].format(**conf['substs']))  for k,w in conf['db'].items() }

class DB(ABC):

    @abstractmethod
    def __init__(self,connection):
        pass

    @abstractmethod
    def __getitem__(self,key):
        pass

    @abstractmethod
    def __setitem__(self,key,value):
        pass

    @abstractmethod
    def pop(self,key):
        pass

    @abstractmethod
    def save(self):
        pass


class JsonDB(DB):

    def __init__(self,connection):
        self.db=read_json(connection)
        self.filename=connection

    def __getitem__(self, key=None):

        if isinstance(key,list):
            try:
                key=list(filter(None, key))
            except TypeError:
                pass

        if key is None:
            return self.db.to_dict()

        return self.db[key].to_dict()

    def pop(self,key):
        item=self[key]
        self.db=self.db.drop(key,axis=1)
        return item

    def __setitem__(self, key=None, value=None):
        value['code']=key
        value=DataFrame([value]).T
        value.columns=[key]
        try:
            self.db=self.db.join(value,how='left')
        except ValueError:
            raise ValueError( f'key {key} exists' )

            #self.db[key]=value

    
    def save(self):
        self.db.to_json(self.filename)

class JsonCache(DB):

    def __init__(self,connection):
        self.cache=read_json(connection,convert_dates=False).set_index(['code','timestamp'])['value'].sort_index()
        self.filename=connection

    def __getitem__(self,key):
        return self.cache[key]

    def __setitem__(self,key,value):
        pass

    def pop(self,key):
        pass

    def save(self):
        self.cache.reset_index().to_json(self.filename,orient='records')

