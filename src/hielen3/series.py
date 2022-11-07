#!/usr/bin/env python
# coding=utf-8
from pandas import DataFrame, Series, concat, DatetimeIndex, Index 
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from numpy import nan, unique, round, inf
from importlib import import_module
from hielen3 import db
from hielen3.utils import isot2ut, ut2isot, agoodtime, uuid as getuuid, dataframe2jsonizabledict
from uuid import UUID
import re
import json
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

        try:
            ser=re.split("\s*>\s*", self.uuid)
            
            if ser.__len__() == 2:
                try:
                    feat=db['features'][ser[0]]
                except Exception as e:
                    feats=db['features'][:]
                    feat=feats[ feats['label'] == ser[0] ]

                fuuid,fname=feat[['uuid','label']].squeeze()
                
                self.feature=fname
                self.uuid=db['features_parameters'][fuuid,ser[1]]['series'].squeeze()
                self.parameter=ser[1]

        except Exception as e:
            raise KeyError (f"Series {self.uuid} not found.")

        series_info=db["series"][self.uuid]
        series_info = dataframe2jsonizabledict(series_info)
        self.__dict__.update(series_info)

        try:
            operands=db["series_operands"][self.uuid].to_dict(orient='index')
        except Exception as e:
            operands={}

        series_info['operands']={ w.pop('label'): w for w in operands.values() }

        self.generator = HSeries._Generator(**series_info, orient=self.orient)

        try:
            t=db['series_thresholds'][self.uuid]
            t=t[['value','color']].reset_index().drop('series',axis=1).set_index('value').sort_index()

            #t=t[['value','color']].reset_index().drop('series',axis=1).to_dict(orient='records')

            self.thresholds=t
        except Exception as e:
            self.thresholds=DataFrame([],
                    columns=['ttype','label','columns'],
                    index=Index([],name='value'),
                    dtype='object')


        self.__loaded__=True


    def __getattr__(self,item):

        self.__delayed_load__()

        return self.__getattribute__(item)
            

    def __init__(self, uuid, orient=None, delayed=True):

        if uuid is None:
            raise ValueError

        self.uuid=uuid
        self.orient = orient or 'data'

        self.feature = None
        self.param = None

        self.__loaded__=False
        if not delayed:
            self.__delayed_load__()

    def clean_cache(self,times=None):
        
        try:
            db['datacache'].pop(key=(self.uuid, times))
        except KeyError as e:
            pass

        try:
            db['events'].pop(key=(self.uuid,times))
        except KeyError as e:
            pass

        self.attribute_update('last',None)
        self.attribute_update('last_event',None)
        self.attribute_update('status',None)


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
                setups['view_range_min']=view_range[0]
            except Exception as e:
                pass
        
            try:
                setups['view_range_max']=view_range[1]
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

        if thresholds is not None and isinstance(thresholds, list):
            for t in thresholds:
                db["series_thresholds"][uuid]=t

        return HSeries(uuid)
    

    def attribute_update(self, attribute=None, value=None):

        if attribute is None:
            return

        db["series"][self.uuid]={attribute:value}

        if self.__loaded__:
            self.__loaded__ = False
            self.__delayed_load__()

    def check(self, cache=None, times=None, geometry=None, **kwargs):

        if cache == 'new':
            times=slice(self.last_event,None,None)
            querycache=None
        else:
            querycache=cache

        aa=self.thresholds

        if aa.empty:

            d=DataFrame(
                    [[self.uuid,self.last,'#','#','#','#','#','#','#']],
                    columns=['series','timestamp','reading_value','threshold_value','ttype','label','color','end','count'])
            return d.set_index(['series','timestamp'])
    
        if aa['ttype'].iloc[0] == 'LOWER':
            aa=concat([aa,DataFrame([[None,'LOWER',None]], index=Index([-inf],name='value'), columns=['label','ttype','color'])]).sort_index()
        
        
        if aa['ttype'].iloc[-1] == 'UPPER':
            aa=concat([aa,DataFrame([[None,'UPPER',None]], index=Index([inf],name='value'), columns=['label','ttype','color'])]).sort_index()

        aa=aa.reset_index()

        bb=aa['value'].copy()

        aa.loc[aa['ttype']=='LOWER',['value','label','color']] = aa.loc[aa['ttype']=='LOWER',['value','label','color']].shift(-1)
        aa.loc[aa['ttype']=='UPPER',['value','label','color']] = aa.loc[aa['ttype']=='UPPER',['value','label','color']].shift(1)
        aa['limit']=bb
        aa=aa[aa['value'].notna()]
        aa.index.name='idt'
        aa=aa.reset_index()

        d=self.data(times=times,cache=querycache,geometry=geometry, **kwargs)

        try:
            d=d.to_frame()
        except Exception as e:
            pass

        v=d.columns[0]

        # TODO capire neither or both
        # TODO separare UPPER e LOWER

        for i in aa.index:
            d.loc[d[v].between(
                min(aa.loc[i,'value'],aa.loc[i,'limit']),
                max(aa.loc[i,'value'],aa.loc[i,'limit']),
                inclusive='neither'
                ),'value']=aa.loc[i,'idt']
    
     
        aa=aa.set_index('idt')

        d=d.reset_index().set_index('value').sort_index()

        d=d.join(aa,how='left').set_index('timestamp').sort_index()[[v,'value','ttype','label','color']]

        d.columns=["reading_value","threshold_value","ttype","label","color"]

        d['series']=v

        d=d.reset_index()

        d=d.replace(nan,"#")

        d['end'] = d['timestamp'].copy()

        d['timestamp']=d[~(d["label"] == d['label'].shift(1)) | ~(d["ttype"] == d['ttype'].shift(1)) ]['end']

        d['timestamp'] = d['timestamp'].pad()


        d=d.set_index('timestamp')

        d['count']=d['label'].groupby('timestamp').count()

        d=d.reset_index()


        d=d[~(d["label"] == d['label'].shift(-1)) | ~(d["ttype"] == d['ttype'].shift(-1)) ]

        d['timestamp']=d['timestamp'].apply(str)


        """
        if lastevent:
            d=d.tail(1)
        """

        #d['feature']=self.feature
        #d['parameter']=self.param
        #d['unit']=self.mu

        def fillth(**kwargs):
            db["events"][{'series':kwargs['series']}]=kwargs
       
        d.apply(lambda x: fillth(**x),axis=1)

        newlast=str(d.tail(1)['timestamp'].squeeze())

        if isot2ut(self.last_event) < isot2ut(newlast):
            try:
                self.attribute_update('last_event',str(d.tail(1)['timestamp'].squeeze()))
                self.attribute_update('status',str(d.tail(1)['label'].squeeze()))
            except Exception as e:
                print ("WARNING SET LAST EVENT ", e)
                pass

        #oldstatus=self.status

        #if not newstatus == oldstatus:
        #    pass
        #    self.attribute_update()



        return d.set_index(['series','timestamp'])




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


        if times is None:
            times=slice(None)

        justnew=False

        try:
            if cache == 'new':
                justnew=True
                timefrom = isot2ut(self.last)
                try:
                    cache=self.cache
                    assert cache in ("active","data")
                except Exception as e:
                    cache="no"
            else:
                timefrom = max(isot2ut(self.first), isot2ut(times.start))

            times=slice(ut2isot(timefrom), times.stop, times.step )


        except Exception as e:
            pass

        firstreqstart=times.start

        out = Series([],name=self.uuid,dtype='float64')

        if cache in ("active","data","old"):
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
                assert not cache == 'old'
                gen = self.generator._generate(times=times,timeref=timeref,geometry=geometry,**kwargs)
                if gen.empty: raise Exception()
            except Exception as e:
                #raise e #DEBUG
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

            out.index.name = "timestamp"

            if cache in ("active","data","refresh"):
                db["datacache"][self.uuid]=out


        except Exception as e:
            #raise e #DEBUG
            pass

        if cache in ("active","data") and not out.empty and not justnew:

            lasttotry=str(out.index[0])
            times=slice(firstreqstart, lasttotry, times.step)

            preout = self.data(times=times,cache="none",geometry=geometry, **kwargs)

            preout.index.name = "timestamp"

            if cache in ("active","data","refresh"):
                db["datacache"][self.uuid]=preout

            if preout.__len__():
                out = concat([preout,out]).sort_index()

        idx = unique(out.index.values, return_index=True)[1]
        out = out.iloc[idx]
        out.index.name = "timestamp"

        if not out.empty:

            self.attribute_update( 'last',  ut2isot(max(isot2ut(self.last), isot2ut(str(out.index[-1])))))


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
                        UUID(value["operand"])
                        self.operands[key]=HSeries(value["operand"],self.orient)
                        continue
                    except Exception as e:
                        pass

                    try:
                        self.operands[key] = json.loads(value["operand"])
                        continue
                    except Exception as e:
                        pass

                    """
                        giving up. Load it "as is".
                        return it
                    """
                    self.operands[key] = value["operand"]

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

            # print (operands) #DEBUG
            #print (self.operator, locals() ) #DEBUG


            return eval(self.operator)


