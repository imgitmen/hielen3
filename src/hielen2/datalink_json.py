#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame, Series, read_json, NaT
from abc import ABC, abstractmethod
from hielen2.utils import loadjsonfile, savejsonfile, newinstanceof, hashfile
from filelock import Timeout, FileLock
from numpy import nan
import json


def dbinit(conf):
    return {
        k: newinstanceof(w.pop("klass"), **w) for k, w in conf["db"].items()
    }


class DB(ABC):
    @abstractmethod
    def __init__(self, connection):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def pop(self, key):
        pass


class JsonDB(DB):
    def __init__(self, connection, schema, lock_timeout_seconds=10):
        self.jsonfile = connection
        self.lock = FileLock(f"{connection}.lock", timeout = lock_timeout_seconds)
        self.md5file = f"{connection}.md5"
        self.md5 = None
        self.schema=schema
        self.__chk_and_reload_jsondb(force=True)

    def __brute_load_jsondb(self):
        try:
            self.db = read_json(self.jsonfile,orient='table',convert_dates=False)
        except Exception as e:
            self.db = DataFrame()

        if self.db.empty:
            self.db=DataFrame({},columns=self.schema['columns'])
            self.db=self.db.set_index(self.schema['primary_key'])

    def __chk_and_reload_jsondb(self, force=False):
        """
        Needs to check for json-database file changes in a thread safe way!!
        """

        md5 = None
        error = None
        try:
            self.lock.acquire()
            try:
                if force:
                    raise FileNotFoundError()

                with open(self.md5file) as o:
                    md5 = o.read()

                if not md5 == self.md5:
                    self.md5 = md5

                self.__brute_load_jsondb()

            except FileNotFoundError as e:
                ## refershing hash
                self.md5 = hashfile(self.jsonfile)
                with open(self.md5file, "w") as o:
                    o.write(self.md5)

                self.__brute_load_jsondb()

            finally:
                self.lock.release()

        except Timeout:
            pass

    def save(self):
        try:
            self.lock.acquire()
            try:
                self.db.to_json(self.jsonfile,orient='table')
                self.md5 = hashfile(self.jsonfile)
                with open(self.md5file, "w") as o:
                    o.write(self.md5)
            finally:
                self.lock.release()
        except Timeout as e:
            # Just to remind Timout error here
            raise e

    def __write_jsondb(self, key, value):
        """
        Needs to lock for writing json-database
        """
        item = None
        error = None
        try:
            self.lock.acquire()
            try:
                self.__chk_and_reload_jsondb()
                if value is None:
                    # Request to remove key, raises KeyError
                    item = self.__getitem__(key)
                    try:
                        self.db = self.db.drop(key, axis=0)
                    except KeyError:
                        raise KeyError(f"key {key} to remove does not exist")
                else:
                    # Request to insert key, raises ValueError

                    primarykey=self.schema['primary_key']
                    
                    if not isinstance(key,(list,set,tuple)):
                        key=[key]

                    if key.__len__() < primarykey.__len__():
                        raise ValueError(f"key {key!r} is not fully determinated")

                    keydict=dict(zip(self.schema['primary_key'],key))
                
                    keydict['value']=value

                    df=read_json(json.dumps([keydict]),convert_dates=False)
                    df=df.set_index(self.schema['primary_key'])

                    try:
                        self.db = self.db.append(df,verify_integrity=True).sort_index()
                    except ValueError as e:
                        raise ValueError(f"key {key} to insert exists")

                    self.db.replace({nan: None, NaT: None}, inplace=True)
                    item = self.__brute_getitem(key)
                self.save()

            except Exception as e:
                error = e
            finally:
                self.lock.release()
        except Timeout as e:
            error = e

        if error is not None:
            raise error

        return item

    def __brute_getitem(self, key=None):

        out=None

        if key is None:
            out=self.db
        else:
            out=self.db.loc[key]

        if isinstance(out,Series):
            out = out.to_frame().T
            out.index.names=self.schema['primary_key']

        out = out.reset_index().to_dict(orient='records')
        if out.__len__() == 1:
            out=out[0]

        return out



    def __getitem__(self, key=None):

        self.__chk_and_reload_jsondb()
        if isinstance(key, list):
            try:
                key = list(filter(None, key))
            except TypeError:
                pass

        return self.__brute_getitem(key)
        

    def pop(self, key):
        return self.__write_jsondb(key, None)

    def __setitem__(self, key=None, value=None):
        self.__write_jsondb(key, value)


class JsonCache(DB):
    def __init__(self, connection):
        self.cache = (
            read_json(connection, convert_dates=False)
            .set_index(["uid", "timestamp"])["value"]
            .sort_index()
        )
        self.filename = connection

    def __getitem__(self, key):
        return self.cache[key]

    def __setitem__(self, key, value):
        pass

    def pop(self, key):
        pass

    def save(self):
        self.cache.reset_index().to_json(self.filename, orient="records")

