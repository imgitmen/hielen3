#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame, Series, concat, DatetimeIndex 
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from numpy import nan, unique, round
from importlib import import_module
from hielen3 import db
from hielen3.utils import isot2ut, ut2isot, agoodtime, uuid as getuuid, dataframe2jsonizabledict
import traceback

def _threadpool(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        return ThreadPoolExecutor().submit(f, *args, **kwargs)

    return wrap


class HSeries:

    def __repr__(self):
        return self.uuid

    def __delayed_load__(self):

        if self.__loaded__:
            return

        series_info = dataframe2jsonizabledict(db["series"][self.uuid])

        self.__dict__.update(series_info)

        try:
            operands=db["series_operands"][self.uuid].to_dict(orient='index')
        except Exception as e:
            operands={}

        series_info['operands']={ w.pop('label'): w for w in operands.values() }

        self.generator = HSeries._Generator(**series_info, orient=self.orient)

        self.__loaded__=True


    def __getattr__(self,item):

        self.__delayed_load__()

        return self.__getattribute__(item)
            

    def __init__(self, uuid, orient=None, delayed=True):

        if uuid is None:
            raise ValueError

        self.uuid=uuid
        self.orient= orient or 'data'
        self.__loaded__=False
        if not delayed:
            self.__delayed_load__()

    def clean_cache(self,times=None):
        db['datacache'].pop(key=(self.uuid, times))


    def setup(
            uuid=None,
            operator=None,
            modules=None,
            cache=None,
            mu=None,
            datatype=None,
            operands=None,
            capability='data',
            first=None,
            valid_range=None,
            view_range=None,
            thresholds=None,
            ):

        def _managed_capabilities_(capability):
            return capability in ['data','map','cloud','stream']

        uuid=uuid or getuuid()

        if isinstance(uuid,HSeries):
            uuid = uuid.uuid

        setups={}

        #TODO gestire le diverse tipologie di dato
        if datatype is not None and datatype in ['numeric']:
            setups['datatable']='geoframe.log'

        if modules is not None and isinstance(modules,dict):
            setups['modules']=modules

        if operator is not None and isinstance(operator, str):
            setups['operator']=operator

        if cache is not None and isinstance(cache, str):
            setups['cache']=cache

        if mu is not None and isinstance(mu, str):
            setups['mu'] = mu

        if capability is not None and _managed_capabilities_(capability):
            setups['capability'] = capability

        if first is not None:
            setups['first'] = first

        if valid_range is not None:
            try:
                setups['valid_range_min']=valid_range[0]
            except Exception as e:
                pass
        
            try:
                setups['valid_range_max']=valid_range[1]
            except Exception as e:
                pass

        if view_range is not None:
            try:
                setups['view_range_min']=valid_range[0]
            except Exception as e:
                pass
        
            try:
                setups['view_range_max']=valid_range[1]
            except Exception as e:
                pass

        db["series"][uuid]=setups
        
        #TODO fare il check di coerenza tra operandi e operatore
        if operands is not None and isinstance(operands,dict):

            table_operands=db["series_operands"]
        
            for k,w in operands.items():

                if not isinstance(w,(list,tuple,dict)):
                    w=[w]

                if isinstance(w,(list,tuple)):
                    wl=min(table_operands.values.__len__(),w.__len__())
                    w=dict(zip(table_operands.values[:wl],w[:wl]))

                    if isinstance(w['operand'],HSeries):
                        w['operand']=w['operand'].uuid

                db["series_operands"][(uuid,k)]=w

        #TODO GESTIRE LE THRESHOLDS: togliere id e mettere primary key (series,label,ttype)
        # 
        # if thresholds is not None and isinstance(thresholds, list):
        #    for t in thresholds:
        #    db["thresholds"][uuid]=t

        return HSeries(uuid)


    @_threadpool
    def thvalues(self, **kwargs):
        return self.__getattr__(self.capability)(**kwargs)


    def data(self, times=None, timeref=None, cache=None, geometry=None, **kwargs):

        if self.capability != 'data':
            raise ValueError( f"{self.uuid} has not 'data' capability" )

        self.__delayed_load__()

        timeref=agoodtime(timeref)

        if cache is None:
            try:
                cache=self.cache
                assert cache in ("active","data")
            except Exception as e:
                cache="no"

        """
        if refresh is not None and refresh and cache in ("active","data"):
            cache = "refresh"
        """

        if times is None:
            times=slice(None)

        try:
            timefrom = max(isot2ut(self.first), isot2ut(times.start))
            times=slice(ut2isot(timefrom), times.stop, times.step )
        except Exception as e:
            pass

        out = Series([],name=self.uuid,dtype='float64')

        if cache in ("active","data"):
            try:
                out = db["datacache"][self.uuid,times]
            except KeyError as e:
                pass

            if isinstance(out,DataFrame):
                out=out[out.columns[0]]

            if not out.empty:
                cachestop = out.index.max()
    
            try:
                timefrom = max(isot2ut(cachestop), isot2ut(times.start))
                times=slice(ut2isot(timefrom), times.stop, times.step )
            except Exception as e:
                pass

        try:

            try:
                gen = self.generator._generate(times=times,timeref=timeref,geometry=geometry,**kwargs)
                if gen.empty: raise Exception()
            except Exception as e:
                #raise e
                gen = DataFrame([],columns=[self.uuid],dtype='float64')

            try:
                gen = gen[gen.columns[0]]
            except AttributeError as e:
                pass

            gen.name=self.uuid

            try:
                gen = round(gen,4) 
            except Exception as e:
                pass

            gen.index=DatetimeIndex(gen.index)

            out = concat([out,gen]).sort_index()

            idx = unique(out.index.values, return_index=True)[1]
            out = out.iloc[idx]
            out.index.name = "timestamp"

            if cache in ("active","data","refresh"):
                db["datacache"][self.uuid]=out

        except Exception as e:
            #raise e
            pass

        return out


    def map(self, times=None, timeref=None, geometry=None, refresh=None, **kwargs):

        if self.capability != 'map':
            raise ValueError( f"{self.uuid} has not 'map' capability" )

        try:
            cache=self.cache
        except Exception as e:
            cache="no"

        if cache is None or cache not in ("active","map"):
            cache = "no"

        if refresh is not None and refresh and cache in ("active","map"):
            cache = "refresh"

        timeref=agoodtime(timeref)

        if timeref is not None:
            cache = "no"

        try:
            
            if cache in ("refresh","no"):
                raise KeyError

            out = db["datacache"][self.uid][times]

            if out.empty:
                raise KeyError


        except KeyError as e:

            try:
                out = self.generator._generate(times=times,timeref=timeref,**kwargs)
                try:
                    out = out[out.columns[0]]
                except AttributeError as e:
                    pass

                if cache not in ("no"):
                    try:
                        db["datacache"][self.uid]=None
                    except KeyError as e:
                        pass
                    finally:
                        db["datacache"][self.uid]=out 

            except Exception as e:
                out = Series()

        out.index.name = "timestamp"

        return out


    def cloud(self, times=None, timeref=None, geometry=None, refresh=None, **kwargs):

        if self.capability != 'cloud':
            raise ValueError( f"{self.uuid} has not 'cloud' capability" )

        try:
            cache=self.cache
        except Exception as e:
            cache="no"

        if cache is None or cache not in ("active","cloud"):
            cache = "no"

        if refresh is not None and refresh and cache in ("active","cloud"):
            cache = "refresh"

        try:
            if cache in ("refresh","no"):
                raise KeyError

            out = db["datacache"][self.uid][times]

            if out.empty:
                raise KeyError

        except KeyError:

            try:
                out = self.generator._generate(times=times,**kwargs)
                try:
                    out = out[out.columns[0]]
                except AttributeError as e:
                    pass

                if cache not in ("no"):
                    try:
                        db["datacache"][self.uid]=None
                    except KeyError as e:
                        pass
                    finally:
                        db["datacache"][self.uid]=out 

            except Exception as e:
                out = Series()

        out.index.name = "timestamp"

        return out
    

    def stream(self, times=None, timeref=None, cache=None, geometry=None, **kwargs):

        if self.capability != 'stream':
            raise ValueError( f"{self.uuid} has not 'stream' capability" )

        self.__delayed_load__()

        timeref=agoodtime(timeref)

        cache="no"

        try:

            try:
                out=self.generator._generate(**kwargs)
                gen = Series([out['queue']],index=[out['timestamp']])
            except Exception as e:
                raise e
                gen = Series([],dtype='object')

            gen.name='queue'
            gen.index=DatetimeIndex(gen.index)
            out = gen[~gen.index.duplicated()]
            out.index.name = "timestamp"

        except Exception as e:
            #raise e
            pass

        try:
            out = out[out.columns[0]]
        except Exception as e:
            pass

        return out

#        return out.to_frame()


    class _Generator:
        def __init__(self, modules=None, operator=None, operands=None, orient=None, **kwargs ):

            self.orient=orient or "data"

            self.modules = {}

            self.operator=operator or "Series([])"

            if not modules is None:
                for k, m in modules.items():
                    self.operator = self.operator.replace(k, f"self.modules[{k!r}]")
                    self.modules[k] = import_module(m)

            self.operands = {}
            
            #OPERANDS RESOLUTION:
            try: 
                for key, value in operands.items():

                    """             
                    trying to extract a series                              
                    """             
                    try:
                        self.operands[key]=HSeries(value["operand"],self.orient)
                        continue
                    except Exception as e:
                        pass

                    """
                        giving up. It should be a scalar.
                        return it
                    """
                    self.operands[key] = value

            except AttributeError as e:
                pass



        def _generate(self, **kwargs):

            operands = kwargs

            operands.update(
                {k: w for k, w in self.operands.items() if not isinstance(w, HSeries)}
            )
        
            runners = { k: w.thvalues(**kwargs) for k, w in self.operands.items()  if isinstance(w, HSeries) }

            operands.update({k: w.result() for k, w in runners.items()})
            #operands.update( { k:w.data(**kwargs) for k,w in self.operands.items() if isinstance(w,HSeries) } )

            ## ATTENZIONE A locals: Implementation Dipendent!!!! ###
            locals().update(operands)
           
            #print (self.operator)
            
            return eval(self.operator)

