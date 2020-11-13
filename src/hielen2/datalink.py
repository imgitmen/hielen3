#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame, read_json
from abc import ABC,abstractmethod 
from hielen2.utils import loadjsonfile, savejsonfile, newinstanceof, hashfile
from filelock import Timeout, FileLock
from numpy import nan

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

class JsonDB(DB):

    def __init__(self,connection,timeout=10):
        self.jsonfile=connection
        self.lock=FileLock(f"{connection}.lock",timeout=10)
        self.md5file=f"{connection}.md5"
        self.md5=None
        self.__chk_and_reload_jsondb(force=True)


    def __chk_and_reload_jsondb(self,force=False):
        '''
        Needs to check for json-database file changes in a thread safe way!!
        '''

        md5=None
        error=None
        try:
            self.lock.acquire()
            try:
                with open(force and '' or self.md5file) as o: md5=o.read()
                if not md5 == self.md5:
                    self.md5=md5
                    self.db=read_json(self.jsonfile)
            except FileNotFoundError as e:
                ## refershing hash
                self.md5=hashfile(self.jsonfile)
                with open(self.md5file,'w') as o: o.write(self.md5)
                self.db=read_json(self.jsonfile)

            finally:
                self.lock.release()
        except Timeout:
            pass

    def save(self):
        try:
            self.lock.acquire()
            try:
                self.db.to_json(self.jsonfile)
                self.md5=hashfile(self.jsonfile)
                with open(self.md5file,'w') as o: o.write(self.md5)
            finally:
                self.lock.release()
        except Timeout as e:
            #Just to remind Timout error here
            raise e

    def __write_jsondb(self,key,value):
        '''
        Needs to lock for writing json-database
        '''
        item=None
        error=None
        try:
            self.lock.acquire()
            try:
                self.__chk_and_reload_jsondb()

                if value is None:
                    #Request to remove key, raises KeyError
                    item=self.db[key].to_dict()
                    self.db=self.db.drop(key,axis=1)
                else:
                    #Request to insert key, raises ValueError
                    value['uid']=key
                    value=DataFrame([value]).T
                    value.columns=[key]
                    self.db=self.db.join(value,how='left')
                    self.db[key].replace({nan: None},inplace=True)
                    item=self.db[key].to_dict()

                self.save()
            except KeyError:
                error = KeyError(f'key {key} to remove does not exist')
            except ValueError:
                error = ValueError( f'key {key} to insert exists' )
            finally:
                self.lock.release()
        except Timeout as e:
            error = e

        if error is not None:
            raise error

        return item


    def __getitem__(self, key=None):

        self.__chk_and_reload_jsondb()
        if isinstance(key,list):
            try:
                key=list(filter(None, key))
            except TypeError:
                pass
        if key is None:
            return self.db.to_dict()
        return self.db[key].to_dict()


    def pop(self,key):
        return self.__write_jsondb(key,None)

    def __setitem__(self, key=None, value=None):
        self.__write_jsondb(key,value)


class JsonCache(DB):

    def __init__(self,connection):
        self.cache=read_json(connection,convert_dates=False).set_index(['uid','timestamp'])['value'].sort_index()
        self.filename=connection

    def __getitem__(self,key):
        return self.cache[key]

    def __setitem__(self,key,value):
        pass

    def pop(self,key):
        pass

    def save(self):
        self.cache.reset_index().to_json(self.filename,orient='records')

