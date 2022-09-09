#!/usr/bin/env python
# coding=utf-8
from abc import ABC, abstractmethod
from importlib import import_module
from hielen3 import db 
from hielen3.utils import uuid as newuuid
from hielen3.series import HSeries
from marshmallow import fields 
from numpy import datetime64, isnat
from pandas import DataFrame
from MySQLdb._exceptions import ProgrammingError


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
        return db['features_type'][ftype]['module'].apply(import_module)


    def __schemata__(mod,actions=None):

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

    def retrive(uuid):
        return HFeature.__featureFactory__(uuid=uuid)

    def update(uuid,**kwargs):
        return HFeature.__featureFactory__(uuid=uuid, **kwargs)

    def retrive_label(label):

        feats=db['features'][:]

        uuid=feats[feats['label']==label]['uuid'].squeeze()

        if isinstance(uuid,str):
            return HFeature.__featureFactory__(uuid=uuid)
        else:
            raise KeyError(f'Single instance of {label!r} not found.')

    def drop(uuid):
        HFeature.retrive(uuid).delete()

    
    def __featureFactory__(uuid=None,ftype=None,**kwargs):
        
        tosetup=uuid is None

        geometry=None

        try:
            if kwargs['geometry']:
                geometry=kwargs['geometry']    
        except KeyError as e:
            pass

        kwargs={k:w for k,w in kwargs.items() if k in db['features'].columns}

        if tosetup:
            if ftype is None:
                raise ValueError("Both uuid and ftype are None")

            kwargs["ftype"]=ftype
            uuid=newuuid()

        if kwargs.__len__():
            try:
                if not kwargs['context']:
                    raise KeyError()
            except KeyError:
                kwargs['context']='no-context'

            db['features'][uuid]=kwargs

        if geometry:
            db['features_geometry'][uuid]={"geometry":geometry}

        feature=db['features'][uuid].to_dict(orient='records')[0]

        try:
            geometry=kwargs['geometry']
            db['features_geometry'][uuid]=geometry
        except KeyError as e:
            pass
        except Exception as e:
            raise ValueError(e)

        out = HFeature.modules(feature['ftype']).squeeze().Feature(feature)

        if tosetup:
            out.setup()

        return out


    class __ParamManager__():

        def __init__(self, uuid):
            self.uuid=uuid
            self.parameters=None

        def set(self,param,ordinal=None,**setups):

            try:
                if self.parameters is None:
                    self.__demand__()

                ser=self[param]

            except KeyError as e:
                ser=None

            try:
                ser.clean_cache()
            except Exception as e:
                pass

            self[param]={"series":HSeries.setup(uuid=ser,**setups), "ordinal":ordinal}

        def __len__(self):

            if self.parameters is None:
                self.__demand__()
            return self.parameters.__len__()

        def __demand__(self):
            try:
                p=db['features_parameters'][self.uuid]['series'].droplevel(['feature'])
                self.parameters=p.apply(HSeries).to_dict()
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

            if isinstance(series,HSeries):
                series=series.uuid

            db['features_parameters'][(self.uuid,param)]={"series":series,"ordinal":ordinal}
            self.__demand__()


        def pop(self,param):
            try:
                out=db['features_parameters'].pop((self.uuid,param))
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
        self.parameters=HFeature.__ParamManager__(self.uuid)
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

class Feature(HFeature):
 
    '''
    Default Feature
    '''
 
    def setup(self,*args,**kwargs):
        pass
 
    def config(self,*args,**kwargs):
        pass

__all__ = ["Feature"]
