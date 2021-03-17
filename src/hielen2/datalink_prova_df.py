#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame, Series, read_json, NaT, read_csv
from abc import ABC, abstractmethod
from hielen2.utils import loadjsonfile, savejsonfile, newinstanceof, hashfile
from filelock import Timeout, FileLock
from numpy import nan
from pathlib import Path
from hashlib import md5
from shutil import rmtree
import os

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

                    value.update(keydict)
                    df = DataFrame([value.values()])
                    df.columns=value.keys()
                    df=df.set_index(self.schema['primary_key'])

                    try:
                        self.db = self.db.append(df,verify_integrity=True).sort_index()
                    except ValueError:
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

'''
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
'''

class seriescode():

    def __init__(self,*args,**kwargs):
        self.h=[ *args ]
        self.h.extend(list(kwargs.values()))
        self.h=''.join([ str(a) for a in self.h])
        self.h = md5( f'{self.h}'.encode() ).hexdigest()

    def __repr__(self):
        return self.h


class fsHielenCache(JsonDB):
    def __init__(self,connection,lock_timeout_seconds=10):
        self.cachepath=connection
        self.lts=lock_timeout_seconds
        schema={"columns":["uid","info"],"primary_key":["uid"]}
        connfile= str( Path(connection) / "index.json")
        super().__init__(connfile, schema, self.lts)

    def __getitem__(self,key):
        info=super().__getitem__(key)
        return CsvCache(self.cachepath,key,self.lts).get(force_reload=True)

    def __setitem__(self,key,value):

        if value is not None and not isinstance(value,(DataFrame,Series)):
            raise ValueError("pandas.DataFrame or pandas.Series required")

        try:
            assert isinstance(key,str)
            assert key.__len__() == 32
        except AssertionError as e:
            raise ValueError(f"key {key} doesn't seems to match requirement format")

        if value is not None:
            super().__setitem__(key,{})
            item=CsvCache(self.cachepath,key,self.lts)
            os.makedirs( item.cachepath , exist_ok=True )
            item.update(value)

            #TODO MAKE STATITICS
            statistics={}
            self.db.loc[key]=statistics

        else:
            super().__setitem__(key,None)
            try:
                item=CsvCache(self.cachepath,key,self.lts)
                item.cleanfs()
            except FileNotFoundError as e:
                pass
    
       
    def update(self,key,value):

        if value is not None and not isinstance(value,(DataFrame,Series)):
        #if value is not None and not isinstance(value,DataFrame):
            raise ValueError("pandas.DataFrame or pandas.Series required")

        if value is not None:
            info=super().__getitem__(key)
            item=CsvCache(self.cachepath,key,self.lts)
            item.update(value)

            #TODO MAKE STATITICS
            statistics={}
            self.db.loc[key]=statistics


class CsvCache(DataFrame):
    def __init__(self, cachepath, item, lock_timeout_seconds=10):

        super().__init__({})

        self.cachepath = Path(cachepath) / item[0:8] / item[8:16] / item[16:24] / item[24:32]
        self.db=None
        self.csv = str( self.cachepath / f"{item}.csv" )
        self.lock = FileLock(f"{self.csv}.lock", timeout = lock_timeout_seconds)
        self.md5file = f"{self.csv}.md5"
        self.md5 = None
        #self.__chk_and_reload_cache(force=True)

    def __brute_load_cache(self):
        try:
            tmpdf = read_csv(self.csv, header=None, sep=";", parse_dates=True)
            super().__init__(tmpdf)
            print ('STOCAZZO')
            print (self)
            print ('CETTESEFREGE')
        except Exception as e:
            pass

    def __chk_and_reload_cache(self, force=False):
        """
        Needs to check for cache file changes in a thread safe way!!
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

                self.__brute_load_cache()

            except FileNotFoundError as e:
                ## refershing hash
                try:
                    self.md5 = hashfile(self.csv)
                    with open(self.md5file, "w") as o:
                        o.write(self.md5)
                except FileNotFoundError as e:
                    pass

                self.__brute_load_cache()
            finally:
                self.lock.release()

        except Timeout:
            pass


    def save(self):
        try:
            self.lock.acquire()
            try:
                self.to_csv(self.csv,header=None,sep=";")
                self.md5 = hashfile(self.csv)
                with open(self.md5file, "w") as o:
                    o.write(self.md5)
            finally:
                self.lock.release()
        except Timeout as e:
            # Just to remind Timout error here
            raise e

    def cleanfs(self):
        try:
            self.lock.acquire()
            try:
                os.unlink(self.csv)
                os.unlink(self.md5file)
                self.drop(self.index,axis=1,inplace=True)
            finally:
                self.lock.release()
        except Timeout as e:
            # Just to remind Timout error here
            raise e


    def update(self, value):
        """
        Needs to lock for writing json-database
        """
        
        try:
            value=value.to_frame()
        except AttributeError as e:
            pass

        value=value.reset_index()
        value.columns=list(range(value.columns.__len__()))
        value=value.set_index(value.columns[0])

        error = None
        try:
            self.lock.acquire()
            try:
                self.__chk_and_reload_cache()
                self.drop(value.index,axis=0,errors='ignore',inplace=True)
                self.append(value,inplace=True).sort_index(inplace=True)
                self.save()
            except Exception as e:
                error = e
            finally:
                self.lock.release()
        except Timeout as e:
            error = e

        if error is not None:
            raise error


    def get(self,force_reload=False):
        self.__chk_and_reload_cache(force=force_reload)
        return self.db


