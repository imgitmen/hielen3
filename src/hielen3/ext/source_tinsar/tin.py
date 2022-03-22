# coding=utf-8

from hielen3.source import CloudSource, ActionSchema, GeoInfoSchema 
from hielen3.utils import LocalFile, ColorMap, Style, FTPPath
from hielen3.ext.source_rawsource import Source as RawSource
import hielen3.api.features as featman
from hielen3.mapmanager import Multiraster
from hielen3.cloudmanager import PotreeCM
from .cloudpainter import makemultilaz
import json
from pathlib import Path
from marshmallow import fields
from numpy import full
from pandas import read_csv, DataFrame, Series, DatetimeIndex
from matplotlib.cm import jet
from matplotlib.colors import rgb2hex
from xarray import open_rasterio
from shutil import copy
import geojson
from datetime import datetime

import traceback


series_file_date_parser = lambda x: datetime.strptime(x, "%d/%m/%Y %H.%M")

#mapbasename="basemap.tif"

class ConfigSchema(GeoInfoSchema):
#class ConfigSchema(ActionSchema):

    _self_hints = {
            "TinSAR Base" : {
                0: ["master_cloud","references to master cloud csv in FTP",True],
                },
            "TinSAR Color Maps": {
                0: ["displ_cmap","Displacement colormap range",True],
                1: ["ampli_cmap","Amplitude colormap range",True],
                },
            "TinSAR Selected Points":{
                0: ["point_style","style code for the selected points",True],
                1: ["series_file","textfile containing selected points and dataseries of theirs",True]
                }
        }
               
            
    master_cloud = FTPPath(required=True, allow_none=False)
    displ_cmap = ColorMap(required=False,allow_none=True,default=None)
    ampli_cmap = ColorMap(required=False,allow_none=True,default=None)
    point_style = Style(required=False, allow_none=True,default=None)
    series_file = FTPPath(required=False, allow_none=True)



class FeedSchema(ActionSchema):

    _self_hints = {
            "TinSAR Feed": {
                0: ["displacement_cloud","reference to result cloud in FTP",True],
                1: ["amplitude_cloud","refernce to radar amplitutde cloud in FTP",True],
                2: ["displacement_geotiff","reference to result geotiff in FTP",True],
                3: ["amplitude_geotiff","refernce to radar amplitude geotiff in FTP",True]
                }
            }
     
    
    displacement_cloud = FTPPath(required=False, allow_none=True)
    amplitude_cloud = FTPPath(required=False, allow_none=True)
    displacement_geotiff = FTPPath(required=False, allow_none=True)
    amplitude_geotiff = FTPPath(required=False, allow_none=True)


def get_imgname(mapname,timestamp,param):
    return f"{mapname}_{timestamp[:14]}_{param}.tif" 

class Source(CloudSource):
    '''
    PhotoMonitoring source manager
    '''

    def _config(self, brandnewconf=True, **kwargs):

        if brandnewconf:
            kwargs['opacity']=50
            
            out=super().config(**kwargs)

            chstruct={
                "param": 'Displacement',
                "struct": {
                    "cache": None,
                    "modules": {},
                    "mu":"mm",
                    "operands": {"output":"displacement"},
                    "operator": None
                    }
                }

            self.addParamSeries(**chstruct)

            chstruct={
                "param": 'Radar_Amplitude',
                "struct": {
                    "cache": None,
                    "modules": {},
                    "mu":"mm",
                    "operands": {"output":"amplitude"},
                    "operator": None
                    }
                }

            self.addParamSeries(**chstruct)
        else:
            out=kwargs


        timestamp=out['timestamp']

        out['master_cloud']=kwargs['master_cloud']

        confpath=self.hasher(timestamp)

        mapmanager=Multiraster(self.uid,confpath)

        mapmanager.mapcache.mkdir()
        
        mapmanager.setMFparams(bands=3,crs='EPSG:4326')

        self.filecache.mkdir(confpath)

        

        #CONFIGURABILI: displ_cmap, ampli_cmap

        def_cmap=[ [ a/100, rgb2hex(jet (a/100)[0:3]) ] for a in range(0,101,10) ]
	
        if kwargs['displ_cmap'] is None:
            kwargs['displ_cmap'] = ColorMap.make_colormap(def_cmap)
            kwargs['displ_cmap']["norm"] = None
        out['displ_cmap']=kwargs['displ_cmap']

        if kwargs['ampli_cmap'] is None:
            kwargs['ampli_cmap'] = ColorMap.make_colormap(def_cmap)
            kwargs['ampli_cmap']["norm"] = None
        out['ampli_cmap']=kwargs['ampli_cmap']

        self.setParamOperands('Displacement',cmap=out["displ_cmap"])

        self.setParamOperands('Radar_Amplitude',cmap=out["ampli_cmap"])

        cloudman=PotreeCM(self.uid,confpath)
        
        cloudman.cloudcache.mkdir()

        clds=makemultilaz(out['master_cloud'],str(self.filecache / confpath ),basemanage='a')

        for k,w in clds.items():
            cloudman.makePotree(w,k)

        #print(json.dumps(out,indent=4))

        out['point_style']=kwargs['point_style']
        try:
            points_file=Path(kwargs["series_file"])
        except Exception as e:
            points_file = None

        self._feed_subitems(points_file,out['point_style'])

        if not brandnewconf:

            ##Ricreare le cloud associate alla config
            try:
                nextconf=self.getActionValues('config',slice(timestamp,None))[1]['timestamp']
            except Exception as e:
                nextconf=None

            feeds=self.getActionValues('feed',slice(timestamp,nextconf))

            for f in feeds:
                feedkwargs=f['value']
                self.feed(**feedkwargs)

        return out


    def config(self,**kwargs):
        return self._config(brandnewconf=True,**kwargs)


    def updateConfig(self,**kwargs):
        return self._config(brandnewconf=False,**kwargs)


    def cleanConfig(self,timestamp):

        """
        da analizzare
        """
        timestamp=self.hasher(timestamp)
        self.filecache.rmdir(timestamp)
        PotreeCM(self.uid,timestamp).cloudcache.rmdir()
        Multiraster(self.uid,timestamp).mapcache.rmdir()


    def _feed_subitems(self, points_file=None,point_style=None):

        try:
            subitems= set(self.getFeatureInfo('subitems'))
        except Exception as e:
            subitems= set([])
         
        """
        associa punti a feature principale e crea serie dati
        """

        if points_file is not None:
            series=read_csv(points_file,sep=";",index_col=0,skiprows=3,parse_dates=[0],date_parser=series_file_date_parser)

            points=read_csv(points_file,sep=";",index_col=0,header=None).head(4).T

            points.columns=list(map(str.lower,points.columns))

            labels=points[[ x for x in points.columns if x not in ['x','y','z']]]

            points = points[['x','y','z']]

            points['label']=labels

            points.columns=['x','y','z','label']

            points['puid']=points['label'].apply(lambda x: self.uid+x)
            
            points=points.set_index("puid")

            for subuid,x,y,z,label in points.itertuples():

                prototype="RawSource"
                properties={
                        "label":self.label+"_"+label,
                        "context":self.context,
                        "style":point_style
                        }
                geometry={
                        "type":"Point",
                        "coordinates":[x,y,z]
                        }


                resp=featman.create_feature(uid=subuid,prototype=prototype,properties=properties,geometry=geometry).status
                resp=int(resp.split(" ")[0]) 

                

                if resp == 201:
                    rs=RawSource(subuid)
                    rs.config(param_list=[["Displacement",0,"mm"]])
                    subitems.add(subuid)

                elif resp == 409:
                    rs=RawSource(subuid)
                    resp=featman.update_feature(uid=subuid,properties=properties,geometry=geometry).status
                    resp=int(resp.split(" ")[0]) 
                    subitems.add(subuid)

                if resp not in (200,201):
                    print (resp)
                    self.setFeatureInfo('subitems',list(subitems))
                    raise ValueError (f"While manageing {label}, '{resp}' occurs")


                rs.feed(input_file=series[label])

            self.setFeatureInfo('subitems',list(subitems))

        return


    def feed(self, **kwargs):

        timestamp=kwargs["timestamp"]
        conf=self.lastActionBefore('config',timestamp)

        timestahash=self.hasher(timestamp)
        reftimehash=self.hasher(conf["timestamp"])

        point_style=conf['point_style']

        subpath=Path(reftimehash, timestahash)

        cloudman=PotreeCM(self.uid,subpath)
        mapmanager=Multiraster(self.uid,reftimehash)

        self.filecache.mkdir(subpath)

        try:
            result_cloud=Path(kwargs["displacement_cloud"])
        except Exception as e:
            result_cloud=None

        if result_cloud is not None:

            r=ColorMap.parse_colormap(conf['displ_cmap'])

            clds=makemultilaz(result_cloud,str(self.filecache / subpath ), basemanage='i',**r)

            for k,w in clds.items():
                result=cloudman.makePotree(w,k)

        try:
            info_cloud=Path(kwargs["amplitude_cloud"])
        except Exception as e:
            info_cloud=None

        if info_cloud is not None:

            r=ColorMap.parse_colormap(conf['ampli_cmap'])

            clds=makemultilaz(info_cloud,str(self.filecache / subpath ), basemanage='i', **r)

            for k,w in clds.items():
                result=cloudman.makePotree(w,k)

        # MAPS #

        mapname=self.hasher(conf['timestamp'])

        try:
            result_tiff=Path(kwargs["displacement_geotiff"])
        except Exception as e:
            result_tiff=None

        if result_tiff is not None:
            imgname=get_imgname(mapname,self.hasher(timestamp),'displacement')
            path_image = mapmanager.mapcache / imgname
            copy(result_tiff,path_image)

        try:
            info_tiff=Path(kwargs["amplitude_geotiff"])
        except Exception as e:
            info_tiff=None


        if info_tiff is not None:
            imgname=get_imgname(mapname,self.hasher(timestamp),'amplitude')
            path_image = mapmanager.mapcache / imgname
            copy(info_tiff,path_image)


        self._timeline_add(timestamp)
        return kwargs


    def updateFeed(self,**kwargs):
        self.cleanFeatureCache()                                                                                                                             
        return self.feed(**kwargs)


    def cleanFeed(self, timestamp):
        timestamp=kwargs["timestamp"]
        conf=self.lastActionBefore('config',timestamp)

        timestahash=self.hasher(timestamp)
        reftimehash=self.hasher(conf["timestamp"])
        subpath=Path(reftimehash, timestahash)
        PotreeCM(self.uid,subpath).cloudcache.rmdir()

        self._timeline_remove(timestamp)


    def data( self, times=None, timeref=None, geometry=None, output="displacement", cmap=None, **kwargs ):

        cmappo=cmap['f_cmap']
        
        if geometry is None:
            return None

        if isinstance(times,slice):
            timestamp=times.stop
        else:
            timestamp=times

        if timestamp is None:
            try:
                timestamp=self.getFeatureInfo('timeline')[-1]
            except Exception as e:
                timestamp = None

        if timestamp is None:
            return None

        conf=self.lastActionBefore('config',timestamp)

        mapname=self.hasher(conf['timestamp'])

        mapmanager= Multiraster(self.uid,mapname)

        mapfile=mapmanager.mapfile

        imgname=get_imgname(mapname,self.hasher(timestamp),output)

        path_image = mapmanager.mapcache / imgname

        name=""

        try:
            with open_rasterio(path_image) as dataset:
                #TODO ricorda dataframe.rio.clip(geometries)
                #print (geometry)
                coords=list(geojson.utils.coords(geometry[0]))

                '''
                if not geographic:
                    coords = list( map( lambda l: [l[0], dataset.y[-1]-l[1]], coords ) )
                '''


                geotype=str(geometry[0]['type'])

                #if isinstance(geometry[0],geojson.Point) :
                if geotype == 'Point':
                    query={
                            'method':'nearest', 
                            **dict(zip(['x','y'],coords[0]))
                            }
                    #name="_".join(map(str,coords[0]))
                    name='nearest'

                #elif isinstance(geometry[0],geojson.Polygon):
                elif geotype == 'Polygon':
                    coords=DataFrame(coords)

                    dirx= dataset.x[0] < dataset.x[-1] and 1 or -1
                    diry= dataset.y[0] < dataset.y[-1] and 1 or -1

                    query={
                            'method':None, 
                            "x":slice(coords[0].min(),coords[0].max(),dirx), 
                            "y":slice(coords[1].min(),coords[1].max(),diry)
                            }
                    name='mean'

                else:
                    raise ValueError("Unmanaged geometry Type")


                selection=dataset.sel(**query)

                color = [
                        int(selection.sel(band=1).mean().round(0)),
                        int(selection.sel(band=2).mean().round(0)),
                        int(selection.sel(band=3).mean().round(0))
                        ]

                result = ColorMap.valorizeColor(cmappo,color)

        except Exception as e:
            return None

        ser=Series([result],index=DatetimeIndex([timestamp]))

        ser.name = name
        return ser


    def map( self, times=None, timeref=None, geometry=None, output="displacement", cmap=None, **kwargs ):

        timestamp=None

        if isinstance(times,slice):
            timestamp=times.stop
        else:
            timestamp=times

        conf=self.lastActionBefore('config',timestamp)

        try:
            mapname=self.hasher(conf['timestamp'])

            mapmanager= Multiraster(self.uid,mapname)

            mapfile=mapmanager.mapfile

            imgname=get_imgname(mapname,self.hasher(timestamp),output)

            path_image = mapmanager.mapcache / imgname

            url = mapmanager.geturl(imgname)

            ser=Series([url],index=DatetimeIndex([timestamp]))
        except Exception as e:
            return None

        return ser


    def cloud( self, times=None, timeref=None, geometry=None, output="displacement", cmap=None, **kwargs ):

        timestamp=None

        if isinstance(times,slice):
            timestamp=times.stop
        else:
            timestamp=times

        if timestamp is None:
            timestamp=self.getFeatureInfo('timeline')[-1]

        conf=self.lastActionBefore('config',timestamp)

        try:
            reftimestamp=timeref or conf['timestamp']

            cloudref=self.hasher(reftimestamp)
            results=self.hasher(timestamp)

            url=PotreeCM(self.uid,cloudref).geturl(results, output) + f"&feature={self.uid}"

            ser=Series([url],index=DatetimeIndex([timestamp]))
        except Exception as e:
            return None

        return ser

