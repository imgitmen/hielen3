#!/usr/bin/env python
# coding=utf-8

from sqlalchemy import create_engine
from pandas import DataFrame, Series, read_json, NaT, read_csv, read_sql, concat, DatetimeIndex, Timestamp
from abc import ABC, abstractmethod
from geojson import Point, loads
from hielen3.utils import loadjsonfile, savejsonfile, newinstanceof, hashfile
from filelock import Timeout, FileLock
from numpy import nan, datetime64
from pathlib import Path
from hashlib import md5
from shutil import rmtree
from json import loads, dumps
from numbers import Number
import os
import re
from crudLib import mongofuncs as mf
from uuid import UUID

def dbinit(conf):

    out={}

    for k,w in conf["db"].items():
        out[k] =  newinstanceof(w.pop("klass"), **w) 

    return out


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
            self.db.replace({nan: None, NaT: None}, inplace=True)
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

        if value is not None and not isinstance(value,Series):
            raise ValueError("pandas.Series required")

        try:
            assert isinstance(key,str)
            assert key.__len__() == 32
        except AssertionError as e:
            raise ValueError(f"key {key} doesn't seems to match requirement format")

        #testing existence (stops if exits)

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
                CsvCache(self.cachepath,key,self.lts).drop()
            except FileNotFoundError as e:
                pass
    
       
    def update(self,key,value):

        if value is not None and not isinstance(value,Series):
        #if value is not None and not isinstance(value,DataFrame):
            raise ValueError("pandas.Series required")

        if value is not None:
            info=super().__getitem__(key)
            item=CsvCache(self.cachepath,key,self.lts)
            item.update(value)

            #TODO MAKE STATITICS
            statistics={}
            self.db.loc[key]=statistics


class CsvCache():
    def __init__(self, cachepath, item, lock_timeout_seconds=10):

        self.cachepath = Path(cachepath) / item[0:8] / item[8:16] / item[16:24] / item[24:32]

        self.db=None
        self.csv = str( self.cachepath / f"{item}.csv" )
        self.lock = FileLock(f"{self.csv}.lock", timeout = lock_timeout_seconds)
        self.md5file = f"{self.csv}.md5"
        self.md5 = None
        #self.__chk_and_reload_cache(force=True)

    def __repr__(self):
        return self.db.__repr__()

    def __brute_load_cache(self):
        try:
            self.db = read_csv(self.csv, header=None, sep=";",index_col=0,parse_dates=True)[1]
        except Exception as e:
            self.db = Series()

        self.db.name="s"

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
                self.db.to_csv(self.csv,header=None,sep=";")
                self.md5 = hashfile(self.csv)
                with open(self.md5file, "w") as o:
                    o.write(self.md5)
            finally:
                self.lock.release()
        except Timeout as e:
            # Just to remind Timout error here
            raise e

    def drop(self):
        try:
            self.lock.acquire()
            try:
                os.unlink(self.csv)
                os.unlink(self.md5file)
                self.db=None
            finally:
                self.lock.release()
        except Timeout as e:
            # Just to remind Timout error here
            raise e


    def update(self, value:Series):
        """
        Needs to lock for writing json-database
        """
        
        error = None
        try:
            self.lock.acquire()
            try:
                self.__chk_and_reload_cache()

                self.db.drop(value.index,errors='ignore',inplace=True)

                value.name='s'

                self.db = self.db.append(value).sort_index()

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


class Mariadb(DB):
 
    geotypes=(
            'point',
            'linestring',
            'polygon',
            'multipoint',
            'multilinestring',
            'multipolygon',
            'geometrycollection',
            'geometry'
            )

   
    @property
    def engine(self):
        def getengine(dialect='mariadb', usr='editor', pwd='rincostocastico', host='127.0.0.1', port=13231, db='geoframe' ):
            connstr='{}://{}:{}@{}:{}/{}'.format(dialect,usr,pwd,host,port,db)
            return create_engine(connstr,echo=False)
        return getengine(**self.conn)


    def __init__(self, connection, table=None, askey=None):
        self.conn = connection

        if table is not None:
            table=table.split(".")
            self.schema=table[0]
            self.table=table[1]

            keysquery=f'''
                select 
                    COLUMN_NAME
                from
                    information_schema.key_column_usage
                where
                    TABLE_SCHEMA = {self.schema!r} and 
                    TABLE_NAME = {self.table!r} and 
                    CONSTRAINT_NAME = 'PRIMARY'
                order by
                    ORDINAL_POSITION
                '''

            columnquery=f'''
                select
                    COLUMN_NAME,
                    COLUMN_TYPE
                from
                    information_schema.columns
                where 
                    TABLE_SCHEMA = {self.schema!r} and 
                    TABLE_NAME = {self.table!r} 
                order by
                    ORDINAL_POSITION
            '''

            e=self.engine
            with e.connect() as connection:
                self.columnstypes = dict(connection.execute(columnquery).all())
                self.keys = [ l[0] for l in connection.execute(keysquery).all() ]
            e.dispose()

            self.columns = list(self.columnstypes.keys())
            self.selectfields= [
                w in 
                Mariadb.geotypes and f"ifnull(st_asgeojson({k}),'null') as {k!r}" or k
                for k,w in
                self.columnstypes.items()
                ]

            if askey is not None:
                if not isinstance(askey,(tuple,list)):
                    askey=[askey]

                self.keys.extend([ k for k in askey if k not in self.keys and k in self.columns ])

            self.values = [ k for k in self.columns if k not in self.keys  ]


    def save(self):
        pass

    @abstractmethod
    def __getitem__(self, key=None):
        pass
  
    @abstractmethod
    def __setitem__(self, key=None, value=None):
        pass

    @abstractmethod
    def pop(self, key):
        pass

class MariadbQuery(Mariadb):
    def __init__(self,connection):
        super().__init__(connection)

    def __getitem__(self, stat=None):

        e=self.engine
        with e.begin() as connection:
            connection.execute('start transaction')
            out = read_sql(
                    stat,
                    connection,
                    coerce_float=True,
                    )
        e.dispose()

        for c in out.columns:
            try:
                out[c] = out[c].apply(loads)
                if out[c].dtype == 'datetime64[ns]':
                    out[c]=out[c].apply(str)
            except Exception as e:
                pass

        return out.copy()

    def __setitem__(self, key, value):
        pass

    def pop(self, stat):
        return self.__getitem__(stat)


class MariadbTable(Mariadb):
    def __init__(self,connection,table,askey=None):
        super().__init__(connection,table,askey)

    def query(self,sqlcond=None):

        stat=f'SELECT {",".join(self.selectfields)} FROM {self.table}'

        if sqlcond is not None and sqlcond.__len__() > 0:
            stat=f'{stat} WHERE {sqlcond}'

        e=self.engine
        with e.begin() as connection:
            connection.execute('start transaction')
            out = read_sql(
                    stat,
                    connection,
                    coerce_float=True,
                    index_col=self.keys
                    )
        e.dispose()

        if out.empty:
            raise KeyError(sqlcond)

        try:
            out=out.to_frame()
        except Exception as e:
            pass

        for c in out.columns:
            try:
                out[c] = out[c].apply(loads)
                if out[c].dtype == 'datetime64[ns]':
                    out[c]=out[c].apply(str)
            except Exception as e:
                pass

        ind=out.index.copy()

        out = out.reset_index()

        out.index=ind

        return out.copy()

    def __getitem__(self, key=None, delete=False):

        templatecond={ w:None for w in self.keys }

        if key is None:
            key=slice(None,None,None)

        def __makekeydict__(k):
            out=templatecond.copy()

            if not isinstance(k,(tuple,list,dict)):
                k=[k]

            if isinstance(k,tuple):
                k=list(k)
            
            if isinstance(k,list):
                keyl=min(self.keys.__len__(),k.__len__())
                k=dict(zip(self.keys[:keyl],k[:keyl]))

            if isinstance(k,dict):
                k={ w:v for w,v in k.items() if w in self.keys}
                out.update(k)

            return out

        if not isinstance(key,(list,tuple,dict)):
            key=[(key,)]

        if isinstance(key,dict):
            key=[key]

        if isinstance(key,tuple) and key.__len__() == 1:
            key=[(key[0],None)]

        if isinstance (key,tuple):
            key=[key]

        conds=[ __makekeydict__(k) for k in list(key) ]

        sqlarr=[]

        for clausule in conds:
            clausulearr=[]
            for cond in clausule.keys():
                if clausule[cond] is not None:
                    if isinstance(clausule[cond],slice):

                        key=clausule[cond]
                        wstart=''
                        con=''
                        wstop=''
            
                        if key.start is not None and key.stop is not None:
                            con='AND'
                        
                        if key.start is not None:
                            wstart=f'{cond} >= {key.start!r}'

                        if key.stop is not None:
                            wstop=f'{cond} <= {key.stop!r}'

                        if key.start is not None or key.stop is not None:
                            sqlcond = f'{wstart} {con} {wstop}'
                            clausulearr.append(sqlcond)

                    elif isinstance(clausule[cond],(list,tuple,set)):
                        condarr=",".join(map(lambda x: f'{x!r}',clausule[cond]))
                        clausulearr.append(f'{cond} in ({condarr})')

                    else:
                        clausulearr.append(f'{cond}={clausule[cond]!r}')

            if clausulearr.__len__():
                sqlarr.append('('+' AND '.join(clausulearr) +')')

        if sqlarr.__len__():
            sqlcond=' OR '.join(sqlarr)
        else: 
            if delete:
                raise KeyError("No condition provided for deletion!")
            sqlcond= 1

        e=self.engine

        with e.begin() as connection:

            stat=f'SELECT {",".join(self.selectfields)} FROM {self.table} WHERE {sqlcond} FOR UPDATE'
            connection.execute('start transaction')
            out = read_sql(
                    stat,
                    connection,
                    coerce_float=True,
                    index_col=self.keys
                    )

            if not out.empty and delete:
                stat = f'DELETE FROM {self.table} WHERE {sqlcond}'
                connection.execute(stat)

        e.dispose()

        if out.empty:
            raise KeyError(sqlcond)

        try:
            out=out.to_frame()
        except Exception as e:
            pass

        for c in out.columns:
            try:
                out[c] = out[c].apply(loads)
                if out[c].dtype == 'datetime64[ns]':
                    out[c]=out[c].apply(str)
            except Exception as e:
                pass

        ind=out.index.copy()

        out = out.reset_index()

        out.index=ind

        return out.copy()

    def __parse_set_kw__(self, key=None, value=None):

        if isinstance(key,slice):
            raise ValueError('slice key not supported')

        if key is None:
            key={}

        if not isinstance(key,(list,tuple,dict)):
            key=[key]

        if isinstance(key,(list,tuple)):
            keyl=min(self.keys.__len__(),key.__len__())
            key=dict(zip(self.keys[:keyl],key[:keyl]))

        if not isinstance(value,(list,tuple,dict)):
            value=[value]

        if isinstance(value,(list,tuple)):
            valuel=min(self.values.__len__(),value.__len__())
            value=dict(zip(self.values[:valuel],value[:valuel]))

        if isinstance(key,dict):
            v=value.copy()

            for k in value.keys():
                if k in self.keys:
                    key[k]=v.pop(k)
            value=v

            key={k:f"{w!r}" for k,w in key.items() if k in self.keys}

            if key.__len__() != self.keys.__len__():
                raise ValueError('table key not full qualified')

        value = { k:w for k,w in value.items() if k in self.values }

        return (key,value)

    def __exec_set_kw__(self, key, value):

        for k in value.keys():
            try:
                if isinstance(value[k],(list,dict,tuple)):
                    value[k]=dumps(value[k])
            except Exception as e:
                pass

            # print (f"{value[k]!r}",value[k].__class__)

            if self.columnstypes[k] in Mariadb.geotypes:
                value[k]=f"ST_GeomFromGeoJSON({value[k]!r})"

            elif value[k] is None:
                value[k] = "NULL"
            else:
                value[k]=f"{value[k]!r}"
       
        print (value)

        if value.__len__():
            columns=','.join([list(*key.keys()),*list(value.keys())])
            values=[*list(key.values()),*list(value.values())]
            updates=", ".join(map(lambda x: f"{x}=VALUE({x})",value.keys()))
        else:
            columns=','.join(key.keys())
            values=list(key.values())
            updates=f"{self.values[0]}={self.values[0]}"

        vvv=",".join(values)

#        stat=f"INSERT INTO {self.table} ({columns}) VALUES ({vvv}) ON DUPLICATE KEY UPDATE {updates}".replace("None","NULL")i
        stat=f"INSERT INTO {self.table} ({columns}) VALUES ({vvv}) ON DUPLICATE KEY UPDATE {updates}"

        print ()


        e=self.engine
        with e.begin() as connection:
            connection.execute(stat)
        e.dispose()



    def __setitem__(self, key=None, value=None):

        key,value = self.__parse_set_kw__(key,value)
        self.__exec_set_kw__(key,value)


    def pop(self, key):
        return self.__getitem__(key,delete=True)


class MariadbHielenGeo(MariadbTable):

    def __init__(self,connection,table,geo_col='geometry',elev_col=None,askey=None):
        super().__init__(connection,table,askey)

        if not geo_col in self.columns:
            raise ValueError(f"colum {geo_col} not in table {self.table}")

        if not self.columnstypes[geo_col] in Mariadb.geotypes:
            raise ValueError(f"colum {geo_col} has not geographic type")

        if elev_col is not None and not elev_col in self.columns:
            raise ValueError(f"colum {elev_col} not in table {self.table}")

        
        if elev_col is None and 'elevation' in self.columns:
            elev_col='elevation'

        self.geo_col=geo_col
        self.elev_col=elev_col


    def __man_na_coords__(xy,z):

        if not isinstance(xy,(list,set,tuple)):
            xy=[0,0]

        return Point([ isinstance(a,Number) and a or 0 for a in [*xy,z]])
            

    def __manage_geo_col__(self,frame=None):

        if frame is not None and self.elev_col is not None:

            xy=frame[self.geo_col].apply(Series,dtype="object")#['coordinates']


            """
            xy=frame[self.geo_col].to_frame().apply(lambda x: 
                    x['geometry'],result_type='expand',axis=1)['coordinates']
            """

            xy=xy['coordinates']

            managed=concat([xy,frame[self.elev_col].replace(nan,0)],axis=1)
            
            frame[self.geo_col]=managed.apply(lambda x: 
                    MariadbHielenGeo.__man_na_coords__(x['coordinates'], x[self.elev_col]), axis=1)
            frame=frame.drop(self.elev_col,axis=1)

        return frame



    def query(self,sqlcond=None):
        frame=super().query(sqlcond)
        try:
            frame=self.__manage_geo_col__(frame)
        except Exception as e:
            pass
        return frame

    def __getitem__(self, key=None, delete=False):
        frame=super().__getitem__(key,delete)
        try:
            frame=self.__manage_geo_col__(frame)
        except Exception as e:
            pass
        return frame

    def __setitem__(self, key=None, value=None):

        key,value = self.__parse_set_kw__(key,value)
    
        try:
            value[self.elev_col]=value[self.geo_col]['coordinates'][2]
        except Exception as e:
            pass
            
        self.__exec_set_kw__(key,value)


class MariadbHielenCache(Mariadb):
    def __init__(self,connection,table):
        super().__init__(connection,table)

    def __parsekey__(key,keysnames:list):

        out = { k:None for k in keysnames }

        if isinstance(key,dict):
            out.update(key)

        if not isinstance(key,(list,slice,tuple)) and key is not None:
            key=[key]

        if isinstance(key,(list,slice)):
            out["series"]=key

        if isinstance(key,tuple):
            key=list(key)
            if not isinstance(key[0],(list,slice)) and key[0] is not None:
                key[0]=[key[0]]
                
            out["series"]=key[0]

            if not isinstance(key[1],(list,slice)) and key[1] is not None:
                key[1]=[key[1]]
                
            out["timestamp"]=key[1]

        return out


    def __setsqlcond__(key,column):

        sqlcond=None

        if isinstance(key,str):
            key=[key]

        if isinstance(key,list):
            key=filter(None,key)
            sqlcond = f"{column} in ({','.join(map(lambda x: f'{x!r}',key))})"

        if isinstance(key,slice):

            wstart=""
            con=""
            wstop=""
            
            if key.start is not None and key.stop is not None:
                con="AND"
            
            if key.start is not None:
                wstart=f"{column} >= {key.start!r}"

            if key.stop is not None:
                wstop=f"{column} <= {key.stop!r}"

            if key.start is not None or key.stop is not None:
                sqlcond = f"{wstart} {con} {wstop}"

        return sqlcond


    def __getitem__(self,key,delete=False):
        """
        WARNING: In case of slice selection with a not None step parmeter
        the deletion process, if requested, not minds the step for row selection
        and all the deleted row will be returned in output.
        """

        key=MariadbHielenCache.__parsekey__(key,self.keys)


        #print (key)

        sercond=MariadbHielenCache.__setsqlcond__(key["series"],"series")
        timecond=MariadbHielenCache.__setsqlcond__(key["timestamp"],"timestamp")

        if sercond is not None and timecond is not None:
            sqlcond=f"{sercond} AND {timecond}"

        if sercond is not None and timecond is None:
            sqlcond=f"{sercond}"

        if sercond is None and timecond is not None:
            sqlcond=f"{timecond}"

        if sercond is None and timecond is None:
            raise KeyError('No condition provided')

        e=self.engine
        with e.begin() as connection:
            stat=f"SELECT * FROM {self.table} WHERE {sqlcond} FOR UPDATE"
            connection.execute('start transaction')
            out = read_sql(
                    stat,
                    connection,
                    coerce_float=True,
                    index_col=['timestamp','series']
                    ).unstack('series').droplevel(0,axis=1)

            if not out.empty and delete:
                stat = f'DELETE FROM {self.table} WHERE {sqlcond}'
                connection.execute(stat)
                e.dispose()
                return out.copy()

        e.dispose()

        try:
            if key["series"] is not None and isinstance(key["series"],slice):
                out=out.T[key["series"]].T

            if key["timestamp"] is not None and isinstance(key["timestamp"],slice):
                out=out[key["timestamp"]]
        except KeyError: 
            raise KeyError(key)

        if out.empty:
            raise KeyError(key)

        return out.copy()

    def __setitem__(self,key,value):

        if value is not None and not isinstance(value,(Series,DataFrame)):
            raise ValueError("pandas.Series or pandas.DataFrame required")

        key=MariadbHielenCache.__parsekey__(key,self.keys)

        try:
            value = value.to_frame()
            value.columns.name='series'
        except Exception as e:
            pass

        if key["series"] is not None:
            if isinstance(key["series"],slice):
                value=value.T[key["series"]].T
            else:
                value=value[key["series"]]

        if key["timestamp"] is not None:
            value=value[key["timestamp"]]
    
        if value is not None and not value.empty:
            value=value.stack()
            value.name='value'
            value=value.reset_index()
            if value.empty:
                return
            value=value[['series','timestamp','value']]
            stat=re.sub(",\($","",re.sub("^","(",value.to_csv(header=None,index=None,quoting=1,lineterminator="),(")))
            stat=f"INSERT INTO {self.table} (series,timestamp,value) VALUES "+stat+" ON DUPLICATE KEY UPDATE value = VALUES(value)"
            e=self.engine
            with e.begin() as connection:
                connection.execute(stat)
            e.dispose()

    def pop(self,key):
        return self.__getitem__(key,delete=True)



class MongodbHielenCache():

    defcon={
            "uri":"mongodb+srv://nivetha:prova@cluster0.cbz69qk.mongodb.net/",
            "db":"MongoTest",
            "col":"Peschiera"
            }


    def __init__(self,connection=None,table=None):
        if connection is None:
            connection = MongodbHielenCache.defcon

        self.uri = connection["uri"]
        self.db = connection["db"]
        self.col = connection["col"]
        self.keys = ['timestamp','series']

    def __parsekey__(key,keysnames:list):

        out = { k:None for k in keysnames }

        if isinstance(key,dict):
            out.update(key)

        if not isinstance(key,(list,slice,tuple)) and key is not None:
            key=[key]

        if isinstance(key,(list,slice)):
            out["series"]=key

        if isinstance(key,tuple):
            key=list(key)
            if not isinstance(key[0],(list,slice)) and key[0] is not None:
                key[0]=[key[0]]
                
            out["series"]=key[0]

            if not isinstance(key[1],(list,slice)) and key[1] is not None:
                key[1]=[key[1]]
                
            out["timestamp"]=key[1]

        return out


    """
    def __setsqlcond__(key,column):

        sqlcond=None

        if isinstance(key,str):
            key=[key]

        if isinstance(key,list):
            key=filter(None,key)
            sqlcond = key[0]

        if isinstance(key,slice):

            wstart=None
            con=""
            wstop=None
           
            if key.start is not None:
                try:
                    wstart= Datetime64(key.start).astype(long)
                except Exception as e:
                    pass

             if key.stop is not None:
                try:
                    wstop= Datetime64(key.stop).astype(long)
                except Exception as e:
                    pass
            
        return sqlcond
    """

    def __getitem__(self,key,delete=False):
        """
        WARNING: In case of slice selection with a not None step parmeter
        the deletion process, if requested, not minds the step for row selection
        and all the deleted row will be returned in output.
        """

        # TODO: manage this function!
        key=MongodbHielenCache.__parsekey__(key,self.keys)
    
        timestart=None
        timestop=None
        series = None


        try:
            timestart = int(datetime64(key['timestamp'].start).astype('datetime64[ns]').astype(int))
            if timestart < 0:
                timestart=None
        except Exception as e:
            pass

        try:
            timestop = int(datetime64(key['timestamp'].stop).astype('datetime64[ns]').astype(int))
            if timestop < 0:
                timestop=None
        except Exception as e:
            pass

        try:
            series = UUID(key['series'][0])
        except Exception as e:
            raise KeyError(key)


        out=mf.fetch(self.uri, self.db, self.col, series, time1= timestart, time2= timestop)
  
    

        if out.empty:
            raise KeyError(key)
            
        dt1=int(out['Timestamp'].iloc[0])
        dt2=int(out['Timestamp'].iloc[-1])

        out.index=DatetimeIndex(out['Timestamp'].apply(Timestamp.fromtimestamp))

        out=out.drop('Timestamp',axis=1)

        out.columns.names=['series']
        out.index.name='timestamp'


        #print (series,dt1,dt2)


        if delete:
            mf.deletes(self.uri, self.db, self.col, series, time1=dt1, time2 = dt2)

        out=out.squeeze().apply(loads).apply(Series)
        out.columns=['x','y','z']

        return out.copy()



    def __setitem__(self,key,value):

        if value is not None and not isinstance(value,(Series,DataFrame)):
            raise ValueError("pandas.Series or pandas.DataFrame required")

        # TODO: Manage it!
        key=MongodbHielenCache.__parsekey__(key,self.keys)

        try:
            value = value.to_frame()
            value.columns.name='series'
        except Exception as e:
            pass

        value.columns=map(str,value.columns)

        # TODO: check for it!
        if key["series"] is not None:
            if isinstance(key["series"],slice):
                value=value.T[key["series"]].T
            else:
                value=value[key["series"]]


        series=UUID(key["series"][0])


        if key["timestamp"] is not None:
            value=value.loc[key["timestamp"]]
    
        #print (value)
        value=value.reset_index()

        value['DATE'] = value['timestamp'].apply(lambda x: (datetime64(x.date()) - datetime64('1970-01-01')).astype('timedelta64[s]').astype(int))
        value['TIME'] = value.apply(lambda x: x['timestamp'].timestamp() - x['DATE'], axis=1)
        value=value.drop('timestamp',axis=1)
        value.columns=['val','DATE','TIME']


        mf.insertUpdate(self.uri, self.db, self.col, value, series)

    
    def pop(self,key):
        return self.__getitem__(key,delete=True)
