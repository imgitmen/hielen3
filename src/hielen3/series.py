#!/usr/bin/env python
# coding=utf-8
import re
import json
import traceback
from functools import wraps
from uuid import UUID
from pandas import DataFrame
from pandas import Series
from pandas import concat
from pandas import DatetimeIndex
from pandas import Index
from pandas import MultiIndex 
from pandas import to_numeric
from numpy import nan
from numpy import unique
from numpy import round
from numpy import inf
from numpy import datetime64
from numpy import timedelta64
from importlib import import_module
from hielen3 import db, conf
from hielen3.utils import isot2ut
from hielen3.utils import ut2isot
from hielen3.utils import agoodtime 
from hielen3.utils import uuid as getuuid
from hielen3.utils import dataframe2jsonizabledict 
from hielen3.contextmanager import family
from concurrent.futures import ThreadPoolExecutor

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

        series_info=db["series"][self.uuid]
        series_info = dataframe2jsonizabledict(series_info)

        if series_info['datatable'] is None or series_info['datatable'] == '':
            series_info['datatable'] = 'datacache'

        try:
            db[series_info['datatable']]
        except Exception as e:
            series_info['datatable'] = 'datacache'

        self.__dict__.update(series_info)
        self.__dict__.pop('modules')
        self.__dict__.pop('operator')

        try:
            operands=db["series_operands"][self.uuid]['operand'].\
                    reset_index().\
                    set_index('label')['operand'].\
                    to_dict()
        except Exception as e:
            operands={}


        try:
            groupmap=db['series_groups'][self.uuid]['ordinal'].\
                    apply(lambda x: f"__GROUPMAP__{str(x).zfill(3)}__").\
                    reset_index().\
                    set_index('ordinal')['element'].\
                    sort_index().\
                    to_dict()
            self.activeuuids=list(groupmap.values())
            self.capability = 'datadiagram'
            series_info['group'] = self.uuid

        except Exception as e:
            groupmap=None
            self.activeuuids=[self.uuid]

        series_info['operands']=operands
        series_info['groupmap']=groupmap

        self.generator = HSeries.__Generator__(**series_info)

        try:
            self.ingroup=db['series_groups'][{"element":self.uuid}]['groupseries'].to_list()
        except Exception as e:
            self.ingroup=None

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
            

    def __init__(self, uuid, delayed=True, **kwargs):

        if uuid is None:
            raise ValueError

        if isinstance(uuid,str):

            try:
                uuid=json.loads(uuid)
            except Exception as e:
                pass
                # print (f"NOTICE: {uuid} seems not a json, {e}") ##DEBUG


        if not isinstance(uuid,dict):
            uuid = str(UUID(uuid))
        else:
            pass
        """
            try:
                context=uuid["context"]
            except KeyError as e:
                context=None

            if context is not None:
                context_family=family(context,homo_only=False)
                if context_family.empty:
                    raise KeyError(f'context {context!r} not found.')
                uuid["context"]=list(context_family["context"])
        """


        try:
            uuid_frame=db["features_parameters_headers_v2"][uuid]
        except KeyError as e:
            raise ValueError(f"series keys {uuid} does not match anything")

        uuid=uuid_frame["series"].drop_duplicates()

        if uuid.__len__() > 1:
            raise KeyError(f"series keys {uuid} matches more than one series. Which is ambiguos")

        self.uuid=str(uuid.squeeze())
        
        self.instances=uuid_frame.set_index(["context","flabel"]).drop(["thresholds","mu","series","parameter"],axis=1)


        """
        self.feature = None
        self.param = None
        """

        self.__loaded__=False
        if not delayed:
            self.__delayed_load__()



    def save_data(self,df):

        # Nota: i tempi vengono gestiti direttamente dal df

        df.index.name='timestamp'
        df.columns.name='series'


        # ATTENZIONE! QUI SI DA PER SCONTATO CHE I VALORI DEL FRAME
        # SINAO NUMERICI. IN FUTURO POTREMO PENSARE DI GENERARE COSE DIVERSE,
        # IN QUEL CASO LE RIGHE FINO ALL'IF VANNO RIVISTE
        try:
            df = df.replace(",",".",regex=True)
        except Exception as e:
            pass

        try:
            df = df.apply(to_numeric,errors='coerce') 
        except Exception as e:
            pass

        try:
            df = df.round(4) 
        except Exception as e:
            pass


        # Check df: Nota
        if df.columns.to_list() == self.activeuuids:
            db[self.datatable][self.activeuuids]=df

            #print("SALVATO:",df.columns)
    
        else:
            raise ValueError("Malformed Frame: ", df)

        return df


    def clean_cache(self,times=None):
      
        if self.cache == 'static':
            return

        to_clean=list(set([self.uuid,*self.activeuuids]))

        try:
            db[self.datatable].pop(key=(to_clean, times))
        except KeyError as e:
            pass

        try:
            db['events'].pop(key=(to_clean, times))
        except KeyError as e:
            pass

        try:
            last=str(db[self.datatable][to_clean].index[-1])
        except Exception as e:
            last=None

        self.attribute_update('last',last)


    def setup(
            uuid=None,
            operator=None,
            modules=None,
            cache=None,
            datatable=None,
            mu=None,
            datatype=None,
            operands=None,
            capability='data',
            first=None,
            valid_range=None,
            view_range=None,
            thresholds=None,
            groupmap=None,
            orient='H'
            ):

        def _managed_capabilities_(capability):
            return capability in ['data','stream','group','datadiagram']

        uuid=uuid or getuuid()

        try:
            uuid = uuid.uuid
        except Exception as e:
            pass

        setups={}

        """
        #TODO gestire le diverse tipologie di dato
        if datatype is not None and datatype in ['numeric']:
            setups['datatable']='geoframe.log'
        """

        if datatable is None:
            datatable = 'datacache'

        try:
            db[datatable]
        except Exception as e:
            # raise e
            datatable='datacache'
            pass

        setups['datatable'] = datatable


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

        # print ("Start_time:",first)
        if first is not None:
            setups['first'] = first

        if orient is not None:
            setups['orient'] = orient

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

            # print (operands)

            table_operands=db["series_operands"]
        
            for k,w in operands.items():

                if not isinstance(w,(list,tuple,set,dict)):
                    w=[w]

                if isinstance(w,(list,tuple,set)):
                    wl=min(table_operands.values.__len__(),w.__len__())
                    w=dict(zip(table_operands.values[:wl],w[:wl]))
                   
                    try:
                        if isinstance(w['operand'],HSeries):
                            w['operand']=w['operand'].uuid
                    except Exception as e:
                        print (w,uuid)
                        #raise (e)

                table_operands[(uuid,k)]=w


        if groupmap is not None:

            try:
                if not isinstance(groupmap,(list,tuple,set)):
                    raise Exception (f"not a vaild list")
           
                print (json.dumps(groupmap,indent=4))

                for i in range(0,groupmap.__len__()):
                    
                    v=groupmap[i].copy()

                    if not isinstance(v,dict):
                        raise Exception (f"{v} has not a valid format")

                    el=v.pop('element')

                    try:
                        el=HSeries(el,delayed=False).uuid
                    except Exception as e:
                        raise e

                    try:
                        v['ordinal']
                    except Exception as e:
                        v['ordinal'] = i

                    try:
                        v['label']
                    except Exception as e:
                        v['label'] = str(i)

                    try:
                        v['tag']
                    except Exception as e:
                        v['tag'] = "EL_"+str(i)

                    db["series_groups"][(uuid,el)]=v

                db["series"][uuid]={"capability":'datadiagram'}

            except Exception as e:
                raise Exception (f"groupmap CONF for {uuid}: {e}")

        if thresholds is not None and isinstance(thresholds, (list,tuple,set)):
            for t in thresholds:
                db["series_thresholds"][uuid]=t

        return HSeries(uuid)
    


    def attribute_update(self, attribute=None, value=None):

        if attribute is None:
            return

        if attribute == 'thresholds':

            if not isinstance(value,(list,set,tuple)):
                value=[value]
            
            for t in value:

                print (t)

                try:
                    t['color'] = re.sub("^##","#",re.sub("^","#",t['color']))
                except Exception as e:
                    pass

                db["series_thresholds"][self.uuid]=t

        if attribute == 'reference':
            pass

        else:
            db["series"][self.uuid]={attribute:value}

        if self.__loaded__:
            self.__loaded__ = False
            self.__delayed_load__()



    def check(self, geometry=None, **kwargs):

        try:
            last_event=db['status'][{'series':self.uuid}].iloc[0]
            last_event_time = str(last_event['last_time'])
        except KeyError as e:
            last_event = None
            last_event_time = None

        
        times=slice(last_event_time,None,None)
        cache='active'


        # BUILDING THE REFERENCE DATAFRAME (aa)
        aa=self.thresholds

        if aa.empty:

            d=DataFrame(
                    [[self.uuid,self.last,'#','#','#','#','#','#','#',0]],
                    columns=['series','timestamp','reading_value','threshold_value','ttype','label','color','end','count','latency'])
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

        # REFEERENCE DATAFRAME DONE

        # EXTRACTING THE DATA
        d=self.data(times=times,cache=cache,geometry=geometry, **kwargs)
        # DATA ESTRACTION DONE

        try:
            d=d.to_frame()
        except Exception as e:
            pass

        v=d.columns[0]

        # TODO capire neither or both
        # TODO separare UPPER e LOWER

        # MATCHING FOR OVERCOMES (each i in aa, thresholds, over d, data)
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

        d['timestamp']=d[~(d["label"] == d["label"].shift(1)) | ~(d["ttype"] == d["ttype"].shift(1)) ]['end']

        d['timestamp'] = d['timestamp'].ffill()

        d=d.set_index('timestamp')

        d['count']=d['label'].groupby('timestamp').count()

        d=d.reset_index()

        d=d[~(d["label"] == d['label'].shift(-1)) | ~(d["ttype"] == d['ttype'].shift(-1)) ]

        reftime = datetime64('now') + timedelta64(conf['server_time_offset'], 'h')

        d['latency']=(reftime-d['end']).astype('timedelta64[s]')

        d['timestamp']=d['timestamp'].astype(str)
        d['end'] = d['end'].astype(str)
        d['latency']=d['latency'].astype(int)

        if not d.empty and last_event is not None:
            d.loc[d.index[0],'count'] = (d.iloc[0]['count'] - 1 + last_event['count']).squeeze()
            d.loc[d.index[0],'timestamp'] = str(last_event['start_time'])

            if d.__len__() > 1:
                if last_event['latency'] is not None:
                    d.loc[d.index[0],'latency'] = last_event['latency']


        def fillth(**kwargs):
            db["events"][{'series':kwargs['series']}]=kwargs
      
        d.apply(lambda x: fillth(**x),axis=1)

        return d.set_index(['series','timestamp'])



    @_threadpool
    def thvalues(self, **kwargs):
        return self.__getattr__(self.capability)(**kwargs)


    def datadiagram(self,**kwargs):
        return self.data(**kwargs)


    def data(self, times=None, timeref=None, cache=None, group=None, geometry=None, **kwargs):

        self.__delayed_load__()
        
        entertimes=times

        if self.capability not in ['data','datadiagram']:
            raise ValueError( f"{self.uuid} has not 'data' capability" )

        if self.ingroup is None: # or group in self.ingroup:
            cangenerate = True
        else:
            cangenerate = False

        timeref=agoodtime(timeref)

        if cache is None or self.cache in ("static"):
            try:
                cache=self.cache
                assert cache in ("active","data","old","static")
            except Exception as e:
                cache="no"
            
        if cache in ("static"):
            cache = "old"
            #TODO
            # va differenziato l'uso di static da serie generate esternamente e serie utilizzate 
            # ancillare come quelle dei riferimenti e dei filtri. Perchè i riferimenti funzionino
            # devono essere estratti completamente. Per questo qui viene settato il times a None
            # side-effect: non si fanno interrogazioni temporali neanche su quelle esterne. MALE!
            times = None

        if times is None:
            times=slice(None,None,None)

        justnew=False

        try:
            if cache == 'new':
                justnew=True

                if self.last is None:
                    timefrom = isot2ut(self.first)
                else:
                    timefrom = isot2ut(self.last) + 1

                try:
                    assert self.cache in ("active","data","old")
                    cache="active"
                except Exception as e:
                    cache="no"
            else:
                tocheck = min(isot2ut(self.last), isot2ut(times.start))
                timefrom = max(isot2ut(self.first), tocheck)

            times=slice(ut2isot(timefrom), times.stop, times.step )
        except Exception as e:
            print ("warning:", e)
            pass

        firstreqstart=times.start

        out = DataFrame([],columns=self.activeuuids,dtype='object')

        # SE E' DA RINFRESCARE LA CACHE ELIMINO QUELLO CHE C'E
        # IN QUESTO MODO ELIMINO ANCHE LE LETTURE CHE NEL NUOVO
        # CALCOLO POTREBBERO RISULTARE NULL
        if cache in ("refresh"):
            self.clean_cache(times)


        # QUESTA PARTE E' DEDICATA AL RECUPERO DEI DATI GIA' PRESENTI
        # NEL DB. NOTA: a questo punto le serie con self.cache = "static"
        # HANNO IL PARAMETRO cache SETTATO AD "old" 
        if cache in ("active","data","old"):
            try:
                out = db[self.datatable][self.activeuuids,times]
                # print ("ESTRATTO:", out.columns)
            except KeyError as e:
                #raise e #DEBUG
                pass

            if not out.empty:
                cachestop = out.index.max()
    
            try:
                timefrom = max(isot2ut(cachestop), isot2ut(times.start))
                times=slice(ut2isot(timefrom), times.stop, times.step )
            except Exception as e:
                pass


        # QUESTA PARTE E' DEDICATA AL CALCOLO DELLE NUOVE LETTURE
        try:
            if cache == 'old': #or not cangenerate:
                raise Exception('request for old, skip generation')

            kwargs['cache'] = cache

            gen = self.generator.__generate__(times=times,timeref=timeref,geometry=geometry,**kwargs)
            #DEBUG print ("APPENA GENERATO:", gen.columns)
            
            if not gen.empty:
                try:
                    gen = gen.to_frame()
                except AttributeError as e:
                    pass

                try:
                    gen.columns=self.activeuuids
                except Exception as e:
                    pass

                gen.index=DatetimeIndex(gen.index)
                
                gen=gen[self.activeuuids]


                if self.valid_range_min is not None:
                    gen=gen.mask(gen<self.valid_range_min,nan)

                if self.valid_range_max is not None:
                    gen=gen.mask(gen>self.valid_range_max,nan)

                gen=gen[gen.notna().any(axis=1)]

                #DEBUG print("LAVORATO GENERATO:",gen.columns)

                if cache in ("active","data","refresh") and cangenerate:

                    gen=self.save_data(gen)

        except Exception as e:
            # print ("WARN series GENERATE: ", e)
            # raise e ##DEBUG
            gen = DataFrame([],columns=self.activeuuids,dtype='object')

        
        if not gen.empty:
            out = concat([ s for s in [out,gen] if not s.empty ],axis=0).sort_index()

        #DEBUG print("GEN UNITO:", out.columns)



        # QUESTA PARTE E' NECESSARIA PER QUESTO MOTIVO:
        # IPOTIZZIAMO CHE I VALORI DELLA SERIE SIANO STATI PRECEDENTEMENTE GENERATI
        # A PARTIRE DA UN CERTO TIMESTAMP "T", SUCCESSTIVO ALLA DATA DI PRIMA LETTURA "F"
        # DICHIARATA PER LA SERIE. DUNQUE TUTTO QUELLO CHE E'CONTENUTO TRA "F" e "T"
        # NON E' ANCORA STATO GENERATO.
        # IN QUESTO CASO, IL PASSAGGIO PRECEDENTE RESTITUISCE SOLO LETTURE DA T IN POI.
        # SE LA RICHIESTA ATTUALE FORINSCE UNA DATA DI PARTENZA "P" TRA "F" E "T", 
        # ALLORA PER SODDIFARE LA CHIAMATA DEVO GENERARE TUTTO QUELLO CHE E' CONTENUTO
        # TRA "P" E "T"
        #
        # SCHEMA:
        #
        #
        #  F----P----T-------
        #
        # ATTENZIONE!
        # TODO ANALISI.
        # PER EVITARE CHIAMATE RICORSIVE INFINITE QUI VIENE RICHIAMATA LA STESSA
        # FUNZIONE "data" CON CACHE = "no" CHE IMPEDISCE DI ENTRARE IN QUESTO IF CHE
        # SEGUE. TUTTAVIA IL RISULTATO POTREBBE NON ESSERE COMPLETO PERCHE', CHIAMANDO
        # LA FUNZIONE TRA "P" e "T" POTREI COMUNQUE RITROVARMI IN UN CASO ANALOGO
        # MA NON NE SONO CERTO. 

        if cache in ("active","data","refresh") and not out.empty and not justnew:

            lasttotry=str(out.index[0])
            times=slice(firstreqstart, lasttotry, times.step)

            kwargs['cache'] = "no"
            preout = self.data(times=times,geometry=geometry, group=group, **kwargs)

            try:
                preout=preout.to_frame()
            except Exception as e:
                pass

            if not preout.empty and cangenerate:
                preout=self.save_data(preout)
            
            if not preout.empty:
                out = concat([ s for s in [preout,gen] if not s.empty ],axis=0).sort_index()

            #DEBUG print("PREOUT UNITO:",out.columns)
        out = out[~out.index.duplicated()]

        if not out.empty and not self.cache in ("static"):
            self.attribute_update( 'last',  ut2isot(max(isot2ut(self.last), isot2ut(str(out.index[-1])))))
            try:
                out=out.loc[entertimes]
            except Exception as e:
                pass

        out=out[self.activeuuids]

        try:
            if out.columns.__len__() < 2:
                out=out.iloc[:,0]
        except Exception as e:
            pass

        return out


    ## WARNING Omesso Map

    ## WARINIG Omesso Cloud

    def stream(self, times=None, timeref=None, cache=None, geometry=None, **kwargs):

        if self.capability != 'stream':
            raise ValueError( f"{self.uuid} has not 'stream' capability" )

        self.__delayed_load__()

        timeref=agoodtime(timeref)

        cache="no"

        try:

            try:
                out=self.generator.__generate__(**kwargs)
                gen = Series([out['queue']],index=[out['timestamp']])
            except Exception as e:
                # print ("WARN series GENERATE: ",e)
                # raise e

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



    #TOLGO ORIENT
    class __Generator__:

        def __load_operand__(value=None):

            #OPERANDS RESOLUTION:
            try:
                return HSeries(value)
            except Exception as e:
                pass

            try:
                value=value.removeprefix('#')
            except Exception as e:
                pass


            """
                trying to load json string, if "value" is it
            """
            try:
                return json.loads(value)
            except Exception as e:
                pass

            return value


            '''
            """
                Trying to get values from a dict, if "out" is it
            """
            try:
                values=out.values()
            except AttributeError as e:
                values=out

            """
                Trying to load suboperands from a list if "values" is it
            """
            try:
                assert not isinstance(values,str)
                values=[ __Generator__.__load_operand__(a,orient) for a in values ]
            except Exception as e:
                pass

            """
                Trying zip a dict, if "out" is it
            """
            try:
                out=dict(zip(out.keys(),values)
            except AttributeError as e:
                out = values

            return out
            '''


        def __init__(self, modules=None, operator=None, operands=None, group=None, groupmap=None, **kwargs ):

            self.modules = {}

            self.group=group

            if operator is None or operator in "__VOID__":
                operator="Series([],dtype='object')"

            self.operator=operator

            if not modules is None:
                for k, m in modules.items():
                    self.operator = self.operator.replace(k, f"self.modules[{k!r}]")
                    self.modules[k] = import_module(m)


            self.operands={
                    k:HSeries.__Generator__.__load_operand__(w) for
                    k,w in operands.items()
                    }

            if groupmap is not None:
                self.groupmap={
                        k:HSeries.__Generator__.__load_operand__(w) for
                        k,w in groupmap.items()
                        }
            else:
                self.groupmap = None
                    

        def __generate__(self, **kwargs):

            try:
                kwargs['times']
            except KeyError as e:
                kwargs['times'] = slice(None,None,None)


            '''
            times=kwargs['times']

            try:
                start=re.sub('\+.*$','',str(times.start))
            except Exception as e:
                start=None

            try:
                stop=re.sub('\+.*$','',str(times.stop))
            except Exception as e:
                stop = None

            kwargs.update({"times":slice(start,stop,times.step)})
            '''
       
            operands = kwargs

            operands.update(
                {k: w for k, w in self.operands.items() if not isinstance(w, HSeries)}
            )

            operands['group'] = self.group

            if self.groupmap is not None:
                groupmap = { k: w.thvalues(**kwargs) for k, w in self.groupmap.items() if isinstance(w, HSeries) }

                groupmap = { k:w.result() for k,w in groupmap.items() }
        
                #groupmap = concat(groupmap,axis=1)

                cols=list(groupmap.keys())

                groupmap= concat(groupmap).unstack().T.sort_index()
                
                try:
                    groupmap.columns = groupmap.columns.droplevel(0)
                except Exception as e:
                    pass

                for c in cols:
                    if c not in groupmap.columns:
                        groupmap[c] = None


                operands['__GROUPMAP__'] = groupmap


            runners = { k: w.thvalues(**kwargs) for k, w in self.operands.items()  if isinstance(w, HSeries) }

            operands.update({k: w.result() for k, w in runners.items()})
            #operands.update( { k:w.data(**kwargs) for k,w in self.operands.items() if isinstance(w,HSeries) } )

            # print (operands) #DEBUG
            # print (self.operator) #DEBUG

            out= eval(self.operator, {"self":self,**operands})            

            return out


