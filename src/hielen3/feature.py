#!/usr/bin/env python
# coding=utf-8
from abc import ABC
from abc import abstractmethod
from importlib import import_module
from hielen3 import db 
from hielen3.series import HSeries
from hielen3.contextmanager import family 
from marshmallow import fields 
from numpy import datetime64
from numpy import isnat
from pandas import DataFrame
from MySQLdb._exceptions import ProgrammingError
from uuid import uuid4 as newuuid
from uuid import UUID

import traceback

def _agoodtime(t):

    try:
        t=datetime64(t)
        assert not isnat(t)
        t=str(t)
    except Exception as e:
        t=None
    return t


class StringTime(fields.DateTime):

    def _deserialize(self, value, attr, data, **kwargs):
        return str(super()._deserialize(value, attr, data, **kwargs))

    def _serialize(self, value, attr, obj, **kwargs):
        return _agoodtime(value)


class HFeature(ABC):

    @abstractmethod
    def config(*args, **kwargs):
        pass


    def modules(ftype=None):
        r = db['features_type'][ftype]['module'].apply(import_module)
        return r


    def __schemata__(mod,actions=None):

        print (mod)

        s=DataFrame(mod.__all__)
        s.columns=['names']
        s=s[s['names'].str.contains("Schema")]
        s.index=s["names"].str.replace("Schema","").str.lower()
        s=s.loc[actions]
        try:
            s=s.to_frame().T
            s.index.name='names'
        except Exception:
            pass

        return s.apply(lambda x: mod.__dict__[x['names']]().__hdict__,axis=1)


    def actions_schemata(ftype=None,actions=None):
        if ftype is None:
            ftype=slice(None)
        if actions is None:
            actions=slice(None)
        s=HFeature.modules(ftype).apply(HFeature.__schemata__,actions=actions).stack()
        s.name='info'
        s=s.reset_index().set_index('label')
        s=s.groupby('label').apply( lambda x: dict(zip(x["names"], x["info"]))).to_dict()
        return s


    @property
    def schemata(self):
        self.__test_del__()
        if self.__actions_schemata__ is None:
            self.__actions_schemata__ = HFeature.actions_schemata(self.ftype)[self.ftype]
        return self.__actions_schemata__


    def create(ftype,**kwargs):
        return HFeature.__featureFactory__(ftype=ftype,**kwargs)


    def retrive(uuid,context=None):
        try:
            return HFeature.__featureFactory__(uuid=uuid)
        except KeyError as e:
            return HFeature.retrive_label(uuid,context)


    def retrive_label(label,context=None):

        if context is not None:
            context_family=family(context,homo_only=False)
            if context_family.empty:
                raise KeyError(f'context {context!r} not found.')

            context=list(context_family["context"])

        try:
            uuid=db['features_info_v2'][{"label":label,"context":context}]["feature"].drop_duplicates()
        except KeyError as e:
            raise KeyError(f'label {label!r} and context {context!r} do not match any row together.')


        if uuid.__len__() > 1:
            found_uuids=list(uuid.values)
            raise KeyError(f'Found multiple instaces for label {label!r} with these UUIDs {found_uuids}.')

        return HFeature.__featureFactory__(uuid=uuid.squeeze())


    def update(uuid,context=None,**kwargs):
        uuid=HFeature.retrive(uuid,context)
        return HFeature.__featureFactory__(uuid=uuid, **kwargs)


    def drop(uuid,context=None):
        uuid=HFeature.retrive(uuid,context)
        HFeature.retrive(uuid).delete()

    
    def __featureFactory__(uuid=None,ftype=None,**kwargs):
        
        tosetup=uuid is None


        kwargs={k:w for k,w in kwargs.items() if k in db['features'].columns}

        if tosetup:
            if ftype is None:
                raise ValueError("Both uuid and ftype are None")

            kwargs["ftype"]=ftype
            uuid=str(newuuid())

        if isinstance(uuid,HFeature):
            uuid = uuid.uuid
        
        try:
            UUID(uuid)
        except ValueError as e:
            raise KeyError( f"Malformed uuid in __featureFactory__: {uuid}"  )

        if kwargs.__len__():
            ## DA ELIMINARE UNA VOLTA DROPPATA LA COLONNA "context" nella tabella Features
            kwargs["context"]="no-context"

            db['features'][uuid]=kwargs

        feature=db['features'][uuid].to_dict(orient='records')[0]

        out = HFeature.modules(feature['ftype']).squeeze().Feature(feature)

        if tosetup: ## SETUP AND RELOAD
            out.setup()
            feature=db['features'][uuid].to_dict(orient='records')[0]
            out = HFeature.modules(feature['ftype']).squeeze().Feature(feature)

        return out


   
    class __ParamManager__():

        def __init__(self, feature):
            self.feature=feature
            self.parameters=None

        def set(self,param,ordinal=None,series_uuid=None,**setups):
            """

            CASO 1) La serie esiste e ma non è associata alla feature (ALIAS in questo caso non riconfiguro - invece sì): OK
            CASO 2) La serie esiste è già associata alla feature e deve essere riconfigurata e NON viene IMPOSTO un id; OK
            CASO 3) Una serie esiste è già associata alla feature con lo stesso label parametro e VIENE IMPOSTO un id; FAIL
            CASO 4) La serie non esiste e deve essere configurata ma viene GENERATO un id: OK
            CASO 5) La serie non esiste e deve essere configurata ma viene IMPOSTO un id: OK

            """
            """
            1) Esiste già associazione
            1.1) uuid in input == uuid presente: OK
                - riconfiguro la serie
            1.2) uuid in input != uuid presente: FAIL
                - alzo l'errore
            2) Non esiste associazione: OK
                - creo oggetto HSeries con uuid in input
            """


            # A questo punto ser_uuid può essere None o un uuid testuale
            alias=True
            managed_series = series_uuid

            clean_cache = series_uuid is None
            #####

            # QUI INSERIRE LA SCELTA DELLA TABELLA IN FASE DI SET

            try:
                setups['datatable']
            except Exception as e:
                try:
                    db[self.feature.context]
                    setups['datatable'] = self.feature.context
                except Exception as e:
                    pass

            #####


            if self.parameters is None:
                self.__demand__()

            try:
                # TEST CASO 1
                assert setups['operator'] == '__ALIAS__'
            except Exception as e:
                alias=False

            if alias:

                managed_series=setups['operands']['__ALIAS__']

                managed_series.__delayed_load__()

                #managed_series=HSeries(setups['operands']['__ALIAS__'], delayed=False)
                #NON DEVE ESSERE RICONFIGURATO IL MODELLO DI CALCOLO
                try:
                    setups.pop('operator')
                except Exception as e:
                    pass

                try:
                    setups.pop('operands')
                except Exception as e:
                    pass

                try:
                    setups.pop('modules')
                except Exception as e:
                    pass
            else:

                try:
                    existing_series=self[param] 
                    assert series_uuid is None or series_uuid == existing_series.uuid
                    managed_series=existing_series
                except AssertionError as e:
                    raise(Exception( f"parameter {param} exists for {self.feature.label} and the linked series has different uuid"  ))
                except KeyError as e:
                    pass

                """
                managed_series può assumere questi valori:
                    1) None, nel caso sia stato fornito series_uuid nullo e non esiste già l'associazione feature/parameter richiesta
                    2) series_uuid nel caso questo sia stato fornito e non esiste l'associazione feature/parameter 
                    3) existing_series (HSeries) nel caso sia stato fornito series_uuid nullo o uguale a quello della serie specificata dall'associazione
                       feature/parameter già esistente

                """

                managed_series=HSeries.setup(uuid=managed_series,**setups)

                try:
                    # SE E' GIA ASSOCIATA ALLA FEATURE CANCELLO CACHE
                    if clean_cache: managed_series.clean_cache()
                except AttributeError as e:
                    pass
           
            # RICONFIURO SERIE

            # QUI ser è completamnte definito
            self[param]={"series":managed_series, "ordinal":ordinal}

        def __len__(self):

            if self.parameters is None:
                self.__demand__()
            return self.parameters.__len__()

        def __demand__(self):
            try:
                p=db['features_parameters'][self.feature.uuid]['series'].droplevel('feature').to_frame()
                p.columns=['uuid']
                self.parameters=p.apply(lambda x: HSeries(**x) ,axis=1).to_dict()

            except KeyError as e:
                self.parameters = {}


        def __getitem__(self, param):
            if self.parameters is None:
                self.__demand__()
            return self.parameters[param]

        def __setitem__(self, param, series):

            try:
                ordinal=series['ordinal']
            except Exception as e:
                ordinal=None

            try:
                series=series['series']
            except Exception as e:
                pass

            try:
                series=series.uuid
            except Exception as e:
                pass

            db['features_parameters'][(self.feature.uuid,param)]={"series":series,"ordinal":ordinal}
            self.__demand__()


        def pop(self,param):
            try:
                out=db['features_parameters'].pop((self.feature.uuid,param))
                self.__demand__()
                return out
            except KeyError:
                return None


        def __repr__(self):
            self.__demand__()
            return self.parameters.__repr__()

        
    def __init__(self, feature):

        if not isinstance(feature,dict):
            try:
                feature=db['features'][feature].to_dict(orient='records')[0]
            except Exception:
                raise ValueError(feature)

        self.__dict__.update(feature)
        self.parameters=HFeature.__ParamManager__(self)
        self.__geometry=None
        self.__deleted__=False
        self.__actions_schemata__=None

    def __test_del__(self):
        if self.__deleted__:
            raise Exception('deleted')

    def __repr__(self):
        self.__test_del__()
        return self.__dict__.__repr__()


    @property
    def geometry(self):
        self.__test_del__()
        if self.__geometry is None:
            try:
                self.__geometry=db['features_geometry'][self.uuid]['geometry'].squeeze()
            except Exception as e:
                self.__geometry = None

        return self.__geometry


    def delete(self):
        self.__test_del__()
        out=self.__dict__
        self.cleanCache()
        self.parameters.pop(None)
        try:
            db['features_geometry'].pop(self.uuid)
        except KeyError as e:
            pass
        db['features'].pop(self.uuid)
        self.__deleted__ = True
        return out

    def truncate_params(self,params=None):
        try:
            p_series=list(self.parameters.pop(params)['series'])
            self.cleanCache(p_series)
        except Exception:
            p_series=[]
            
        return p_series

    def cleanCache(self,params=None):
        self.__test_del__()
        try:
            params=db['features_parameters'][self.uuid,params]['series'].values
            return db['datacache'].pop(list(params))
        except KeyError:
            return None


    def execute(self,action,**kwargs):
        self.__test_del__()
        try:
            mod=import_module(self.__module__)
            klass=mod.__getattribute__(f"{action.capitalize()}Schema")
            kwargs=klass().load(kwargs)
            return self.__getattribute__(action)(**kwargs)
        except Exception as e:
            raise e
        
    @abstractmethod
    def setup(self,*args,**kwargs):
        pass


    """

    def getActionValues(self,action=None,timestamp=None):
        if action is None:
            action=slice(None,None)
        if timestamp is None:
            timestamp=slice(None,None)
        try:
            
            out = db['actions'][self.uid,action,timestamp]
            if not isinstance(out,list):
                out = [out]
        except KeyError:
            return []

        return out

    def lastActionBefore(self,action,timestamp=None):
        c=self.getActionValues(action,slice(None,timestamp,None))
        try:
            c=c[-1]
            try:
                return c['value']
            except KeyError:
                return c

        except Exception as e:
            return None

    def deleteActionValues(self, action=None, timestamp=None):
        out=self.getActionValues(action,timestamp)

        if not isinstance(out,list):
            out=[out]

        for act in out:

            a=act['action']
            t=act['timestamp']
        
            try:
                self.__getattribute__(f"clean{a.capitalize()}")(t)
            except Exception as e:
                traceback.print_exc()
                pass
            
            try:
                db['actions'][self.uid,a,t]=None
            except Exception as e:
                raise ValueError(e)

        return out


    """

