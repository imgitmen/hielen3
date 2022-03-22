#!/usr/bin/env python
# coding=utf-8
from glob import glob
from pathlib import Path, os
from inspect import ismodule
from abc import ABC, abstractmethod
from importlib import import_module
from hielen3 import db, conf
from hielen3.mapmanager import Multiraster
from hielen3.sourcestorage import SourceStorage
from hielen3.utils import getSchemaDict, LocalFile, FTPPath, hasher
from marshmallow import Schema, fields, ValidationError, INCLUDE
from numpy import datetime64, isnat, full, log
import rasterio
from rasterio.warp import transform_bounds, transform_geom
import magic
import re

import traceback

def loadModule(proto):
    if ismodule(proto):
        return proto

    mod=db["features_proto"][proto]["module"]

    try:
        return import_module(mod)
    except Exception as e:
        return proto

def moduleActions(proto):
    mod=loadModule(proto)

    try:
        return [ k.replace('Schema','').lower() for k in mod.__dict__.keys() if 'Schema' in k ]
    except Exception as e:
        return []

def getActionSchemaClass(proto, action):
    mod=loadModule(proto)
    return mod.__getattribute__(f"{action.capitalize()}Schema")

def getActionSchema(proto, action):
    return getSchemaDict(getActionSchemaClass(proto, action)())

def sourceFactory(feat):
    if isinstance(feat, str):
        feat=db['features'][feat:feat]

    return loadModule(feat['type']).Source(feature=feat)


class StringTime(fields.DateTime):

    def _deserialize(self, value, attr, data, **kwargs):
        return str(super()._deserialize(value, attr, data, **kwargs))

    def _serialize(self, value, attr, obj, **kwargs):
        return _agoodtime(value)



class ActionSchema(Schema):
    '''
    Minimal ActionSchema object. Used to define at least a timestamp
    '''

    class Meta:
        unknown = INCLUDE

    _self_hints={
            "Base": {
                0: ["timestamp","Reference time" ,0]
                }
            }

    @property
    def hints(self):
        out = self.__class__._self_hints
        for c in self.__class__.__bases__:
            try:
                out.update(c().hints)
            except AttributeError as e:
                pass
        return out

    timestamp = StringTime(required=True, allow_none=False)

class GeoInfoSchema(ActionSchema):
    '''
    Minimal map based ActionSchema object. Used to define geo-info
    '''
    _self_hints = {
            "Geo Info": {
                0: ["master_image","The base image used as reference grid for elaboration or basemap. It can be any image format managed by rasterio pyhton library (GeoTIFF, jp  eg, ...). Colometric interpretation will be RGB whit Black alpha mask. Any elaboration image based on the 'master_image' will share geometry and reference system with it.",False],
                1: ["geo_reference_file","Reference file for the geolocalization of the 'grid' and all the dependent elaboration images. It can be a standard world file (six lines text file) according to http://www.kralidis.ca/gis/worldfile.htm, as well an '.aux.xml' file according to https://desktop.arcgis.com/en/arcmap/10.3/manage-data/raster-and-images/auxiliary-files.htm (just the Coordinate system, the Transformation and the Projection informations are here managed). NOTE: When a valid 'geo_regerence_file' is provided, therein informations overwrite the ones possibly embedded into the 'master_image'",False],
                2:["crs", "the Coordinate Reference System of the master_image in the string form 'autority:code' (i.e.: 'EPSG:3857'). NOTE: If a valid 'crs' is provided, this value overwrites the ones possibly provided with the 'geo_regerence_file' and/or embeded into the 'master_image'",False],
                3:["extent_easting","Easting map extention, according with 'crs' and 'geo_reference_file'. Ignored if 'master_image' is provided",False],
                4:["extent_northing","Northing map extention, according with 'crs' and 'geo_reference_file'. Ignored if 'master_image' is provided",False]
                }
            }

    master_image = FTPPath(required=False, allow_none=True)
    geo_reference_file = FTPPath(required=False,default=None, allow_none=True)
    crs=fields.Str(required=False,default=None,allow_none=True)
    extent_easting=fields.Number(required=False, default=None, allow_none=True, as_string=False)
    extent_northing=fields.Number(required=False, default=None, allow_none=True, as_string=False)



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


class HielenSource(ABC):

    def __init__(self, feature):

        if isinstance (feature,str):
            feature=db['features'][feature]

        self.__dict__.update(feature)
        self.module = import_module(self.__module__)
        self.incomepath=conf['incomepath']

        #TODO possibili problemi di sicurezza
        self.filecache = SourceStorage(conf['syscache']['filecache'],self.uid)

    def hasher(self,*args,**kwargs):                                                                                                                         
        h=[ *args ]
        h.extend(list(kwargs.values()))
        h=''.join([ str(a) for a in h])
        return re.sub("[^\d]","",h)  

    def execAction(self,action,**kwargs):

        aclass=getActionSchemaClass(self.module,action)
        try:
            kwargs=aclass().load(kwargs)
            return self.__getattribute__(action)(**kwargs)
        except Exception as e:
            raise e
            #raise ValueError(e)

    def updateAction(self,action,**kwargs):
        aclass=getActionSchemaClass(self.module,action)
        try:

            out=self.getActionValues(action,kwargs['timestamp'])[0]['value']
            
            for k,w in kwargs.items():
                if w is not None:
                    out[k]=w

            kwargs=aclass().load(out)

            return self.__getattribute__(f"update{action.capitalize()}")(**kwargs)
        except Exception as e:
            raise e
            #raise ValueError(e)

    def getFeatureInfo(self,info):
        return db["features_info"][self.uid][info]

    def setFeatureInfo(self,info,value):
        feat_info = db["features_info"][self.uid]
        feat_info[info]=value
        db['features_info'][self.uid]=None
        db['features_info'][self.uid]=feat_info

    def cleanFeatureCache(self,params=None):
        fpars=list(db["features_info"][self.uid]['parameters'].values())

        if params is None:
            params = fpars
           
        if not isinstance(params,list):
            params = [params]

        params=[ a for a in fpars if a in params ]

        for p in params:
            try:
                db["datacache"][p]=None
            except KeyError as e:
                pass


    def getActionSchema(self,action):
        return getActionSchema(self.module,action)

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


    def retriveSeries(self,parameters):

        ft = db["features_info"][self.uid]
           
        try:
           
            if parameters is None:
                series = list(ft["parameters"].values())
            else:
                series = [ft["parameters"][parameters]]
           
        except KeyError as e:
            raise KeyError(  str(e) + " not found"  )

        return series


    def addParamSeries(self,param,struct):

        suid=hasher(self.uid,param)

        try:
            db['series'][suid] = None
        except KeyError:
            pass

        struct['operands']['source']=self.uid

        db['series'][suid]=struct

        try:
            params=self.getFeatureInfo('parameters')
        except KeyError as e:
            params={}



        params.update({param : suid})

        self.setFeatureInfo('parameters',params)
    

    def setParamOperand(self,param,operand,value):
        serid=self.retriveSeries(param)
        ser=db['series'][serid]
        ser['operands'][operand]=value
        db['series'][serid]=None
        db['series'][serid]=ser
        db['series'].save()


    def setParamOperands(self,param,**kwargs):
        serid=self.retriveSeries(param)
        ser=db['series'][serid]

        for k,w in kwargs.items():
            ser['operands'][k]=w

        db['series'][serid]=None
        db['series'][serid]=ser
        db['series'].save()


    def _timeline_add(self,timestamp):

        timestamp=_agoodtime(timestamp)

        if timestamp is None:
            raise ValueError(timestamp)

        try:
            timeline=set(self.getFeatureInfo('timeline'))
            if timeline is None:
                raise KeyError
        except Exception as e:
            timeline = set([])

        timeline.add(timestamp)

        timeline=list(timeline)
    
        timeline.sort()

        self.setFeatureInfo('timeline',timeline)


    def _timeline_remove(self,timestamp):

        timestamp=_agoodtime(value)

        if timestamp is not None:
            try:
                timeline=self.getFeatureInfo('timeline')
                timeline.pop(timeline.index(timestamp))
                self.setFeatureInfo('timeline',timeline)
            except Exception as e:
                #traceback.print_exc()
                pass


class DataSource(HielenSource):
    @abstractmethod
    def data(**kwargs):
        pass

class MapSource(DataSource):

    mapbasename="basemap.tif"

    def _set_map_info(self, map_info):
        try:
            feature_info=db['features_info'][self.uid]
            feature_info['map']=map_info
            db['features_info'][self.uid]=None       
            db['features_info'][self.uid]=feature_info
        except Exception as e:
            #traceback.print_exc()
            pass

    def config(self, **kwargs):

        timestamp=kwargs['timestamp']                                                                                                                        
        mapname=self.hasher(timestamp)
        temp_base_file=kwargs['master_image']
        temp_georef_file=kwargs['geo_reference_file']
        extent=[ kwargs['extent_northing'], kwargs['extent_easting'] ]
        crs=kwargs['crs']
        mapmanager=Multiraster(self.uid,mapname)
        mapbase =  mapmanager.mapcache / MapSource.mapbasename
        mapmanager.mapcache.mkdir()
        try:
            opacity=int(kwargs['opacity']/100*255)
        except Exception as e:
            opacity=255

        try:
            temp_base_name_parts=str(temp_base_file).split(".")

            #Temporary georef file
            with open(temp_georef_file) as trf:
                '''
                trying to match reference file type (wld or aux.wml) if exists
                '''
                try:
                    float(trf.readline())
                    def_georef_file=Path(".".join([*temp_base_name_parts[0:-1],"wld"]))
                except Exception as e:
                    def_georef_file=Path(".".join([*temp_base_name_parts,"aux","xml"]))

                temp_georef_file.replace(def_georef_file)

        except Exception as e:
            #traceback.print_exc()
            pass

        try:
            '''
            trying to define crs from income parameters
            '''
            crs=rasterio.crs.CRS.from_string(crs)
        except Exception:
            crs=None

        geographic=True
    
        defaultmeta={ 
            "driver":"GTiff",
            "count":4,
            "compress":"lzw",
            "dtype":"uint8"
            }
            
        try:
            try:
                src=rasterio.open(temp_base_file)
            except Exception as e:

                #traceback.print_exc()

                try:
                    src.close()
                except Exception:
                    pass

                if extent[0] is None or extent[1] is None:
                    return { 'timestamp': timestamp, 'master_image': None, 'meta': None }


#                    raise ValueError('Unable to define map extention: not "master_image" nor "extentions" defined')

                h = int(extent[1])
                w = int(extent[0])
                count=4

                imgout=full([w,h,count],dtype='uint8',fill_value=[255,255,255,0])

                with rasterio.open(temp_base_file, 'w', height=h, width=w, **defaultmeta) as dst:
                    for i in range(0, count):
                        dst.write(imgout[:,:,i],i+1)

                src=rasterio.open(temp_base_file)

            meta = src.meta.copy()

            meta.update(defaultmeta)

            if crs is not None:
                meta['crs']=crs

            meta['transform']=list(meta['transform'])[0:6]

            try:
                meta['crs']=meta['crs'].to_string()
            except AttributeError:
                geographic=False
                meta['crs']='EPSG:3857'

               
            if src.count == 1:
                #trasformare da gray scale a rgba
                rgb = src.read(1).copy()
                rgb = (rgb/2**16)*255
                rgb = rgb.astype("uint8")
                rgb = [rgb,rgb,rgb]
            else:
                rgb = []
                for i in range(0, src.count):
                    rgb.append(src.read(i+1))

            if rgb.__len__() == 3:
                rgb.append( full(rgb[0].shape,dtype="uint8",fill_value=opacity) )

            minlon,minlat,maxlon,maxlat = transform_bounds(meta['crs'],'EPSG:4326',*src.bounds)

            with rasterio.open(mapbase, 'w', **meta) as dst:
                for i in range(0, rgb.__len__()):
                    dst.write(rgb[i],i+1)

                bands=dst.meta['count']
                outcrs=dst.meta['crs']

            if outcrs is None or outcrs.linear_units== 'UNKNOWN':
                outum = 'METERS'
            else:
                outum=outcrs.linear_units

        except Exception as e:
            raise e
        finally:
            try:
                src.close()
            except Exception:
                pass



        #Master_image is ok. Making mapfile
        mapmanager.setMFparams(bands=bands,crs=outcrs,um=outum)

        self._set_map_info({
            "extent":{
                "minlon":minlon,
                "minlat":minlat,
                "maxlon":maxlon,
                "maxlat":maxlat,
                },
            "center":{
                "lon":(maxlon+minlon)/2,
                "lat":(maxlat+minlat)/2
                },
            "zoom":{
                "default":round( log (40075017 / max( maxlon-minlon, maxlat-minlat) )  / log(2)) -15 
                },
            "basemapurl": mapmanager.geturl(MapSource.mapbasename),
            "geographic": geographic 
            })                 


        out={}

        out['timestamp']=timestamp
        out['meta']=meta

        kwargs.update(out)

        return kwargs


    @abstractmethod
    def map(timefrom=None, timeto=None, geom=None, **kwargs):
        pass


class CloudSource(MapSource):

    @abstractmethod
    def cloud(timefrom=None, timeto=None, geom=None, **kwargs):
        pass
