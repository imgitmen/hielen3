# coding=utf-8

from hielen3.source import MapSource, ActionSchema, GeoInfoSchema 
from hielen3.utils import LocalFile, ColorMap, loadjsonfile, FTPPath
from hielen3.mapmanager import Multiraster
import rasterio
import json
from rasterio.warp import transform_bounds, transform_geom
import magic
import os
import re
from pathlib import Path
from .struct import config_NC, feed_NC, clean_feed_NC, generate_map, extract_data 
from marshmallow import fields
from numpy import arange, full, zeros, log
from pandas import read_csv, DataFrame, Series, DatetimeIndex
import traceback


class ConfigSchema(GeoInfoSchema):

    _self_hints = {
            "PhotoMonitoring Base" : {
                0: ["param_file","The parameters.json file used for retrive 'step_size', 'window_size', 'cc_thresh'",True],
                },
            "PhotoMonitoring Color Maps": {
                0: ["ns_cmap","East-Weast colormap range",True],
                1: ["ew_cmap","Nord-South colormap range",True],
                2: ["displ_cmap","Displacement colormap range",True],
                3: ["cc_cmap","Correlation Coefficient mask color map",True],
                4: ["ch_cmap","Change Detection mask color map",True]
                }
        }
               
    param_file = FTPPath(required=False, allow_none=True)

    ew_cmap=ColorMap(required=False,allow_none=True,default=None)
    ns_cmap=ColorMap(required=False,allow_none=True,default=None)
    displ_cmap=ColorMap(required=False,allow_none=True,default=None)
    cc_cmap=ColorMap(required=False,allow_none=True,default=None)
    ch_cmap=ColorMap(required=False,allow_none=True,default=None)


class FeedSchema(ActionSchema):

    _self_hints = {
            "PhotoMonitoring Feed": {
                0: ["NS_displacement","textfile containing the grid of the North-South displacement.",True],
                1: ["EW_displacement","textfile containing the grid of the East-Weast displacement.", True],
                2: ["CORR","textfile containing the grid of the correlation coefficents.", True],
                3: ["CHANGE","textfile containing the grid of the change detection.", True]
                }
            }
    
    NS_displacement = FTPPath(required=False, allow_none=True)    
    EW_displacement = FTPPath(required=False, allow_none=True)    
    CORR = FTPPath(required=False, allow_none=True)
    CHANGE = FTPPath(required=False, allow_none=True)


class Source(MapSource):
    '''
    PhotoMonitoring source manager
    '''

    def ncfile(self,timestamp):
        return self.filecache / f"{self.hasher(timestamp)}.nc"


    def config(self, **kwargs):

        out=super().config(**kwargs)
        try:
            pars=loadjsonfile(kwargs["param_file"])
        except Exception as e:
            #traceback.print_exc()
            pass

        try:
            x_offset=y_offset= pars['window_size']
        except Exception:
            x_offset=y_offset=kwargs['window_size'] or 1

        x_offset=int(x_offset/2)
        
        try:
            step_size=pars['step_size']
        except Exception:
            step_size=kwargs['step_size'] or 1

        try:
            nthr=pars['CCthreshold'] or 0
        except Exception:
            nthr=kwargs['ccthreshold'] or 0
        
        nthr=max(nthr,0)

        out['step_size']=step_size
        out['window_size']=x_offset
        out['ccthreshold']=nthr

        meta=out['meta']

        timestamp=out['timestamp']


        #x_values=arange(step_size,step_size+meta['width']-y_offset,step_size)
        #y_values=arange(step_size,step_size+meta['height']-x_offset,step_size)

        x_values=arange(step_size,step_size+meta['width'],step_size)
        y_values=arange(step_size,step_size+meta['height'],step_size)
        #deg2met=4.4915764206e-06

        x_values=x_values*meta['transform'][0]+meta['transform'][2]
        y_values=y_values*meta['transform'][4]+meta['transform'][5]

        """
        if self.getFeatureInfo('map')['geographic']:
            x_values=x_values*meta['transform'][0]+meta['transform'][2]
            y_values=y_values*meta['transform'][4]+meta['transform'][5]
        else:
             x_values=x_values*deg2met
             y_values=y_values*deg2met
        """


        self.filecache.mkdir()
        ncpath=self.ncfile(timestamp)

        config_NC(ncpath,timestamp,x_values,y_values).close()

        ew_cmap=kwargs['ew_cmap'] or ColorMap.make_colormap()
        ns_cmap=kwargs['ns_cmap'] or ColorMap.make_colormap()
        displ_cmap=kwargs['displ_cmap'] or ColorMap.make_colormap()
        cc_cmap=kwargs['cc_cmap'] or ColorMap.make_colormap([[0,"#00FF00"],[1,"#FF0000"]])
        ch_cmap=kwargs['ch_cmap'] or ColorMap.make_colormap([[0,"#00FF00"],[1,"#FF0000"]])

        mu = self.getFeatureInfo('map')['geographic'] and "m" or "mm"

        self.setParamOperands('East-West_Displacement',cmap=ew_cmap, mu=mu)
        self.setParamOperands('North-South_Displacement',cmap=ns_cmap, mu=mu)
        self.setParamOperands('Displacement', cmap=displ_cmap, mu=mu)
        self.setParamOperands('Correlation_Coefficient', cmap=cc_cmap, mu=mu)
        self.setParamOperands('Change_Detection', cmap=ch_cmap, mu='')

        kwargs.update(out)

        #print(json.dumps(out,indent=4))

        return kwargs

    def updateConfig(self,**kwargs):

        ew_cmap=kwargs['ew_cmap'] or ColorMap.make_colormap()
        ns_cmap=kwargs['ns_cmap'] or ColorMap.make_colormap()
        displ_cmap=kwargs['displ_cmap'] or ColorMap.make_colormap()
        cc_cmap=kwargs['cc_cmap'] or ColorMap.make_colormap([[0,"#00FF00"],[1,"#FF0000"]])
        ch_cmap=kwargs['ch_cmap'] or ColorMap.make_colormap([[0,"#00FF00"],[1,"#FF0000"]])

        mu = self.getFeatureInfo('map')['geographic'] and "m" or "mm"

        self.setParamOperands('East-West_Displacement',cmap=ew_cmap, mu=mu)
        self.setParamOperands('North-South_Displacement',cmap=ns_cmap, mu=mu)
        self.setParamOperands('Displacement', cmap=displ_cmap, mu=mu)
        self.setParamOperands('Correlation_Coefficient', cmap=cc_cmap, mu=mu)
        self.setParamOperands('Change_Detection', cmap=ch_cmap, mu='')
        
        self.cleanFeatureCache()

        return kwargs 

    def cleanConfig(self,timestamp):
        timestamp=self.hasher(timestamp)
        os.unlink(self.ncfile(timestamp))
        Multiraster(self.uid,timestamp).mapcache.rmdir()
        self.cleanFeatureCache()


    def feed(self, **kwargs):

        frames={}

        try:
            frames['ch']= read_csv(Path(kwargs["CHANGE"]),header=None)
        except Exception as e:
            frames['ch']=None

        try:
            frames['ns']= read_csv(Path(kwargs["NS_displacement"]),header=None)
        except Exception as e:
            frames['ns']=None

        try:
            frames['ew']= read_csv(Path(kwargs["EW_displacement"]),header=None)
        except Exception as e:
            frames['ew']=None

        try:
            frames['corr']= read_csv(Path(kwargs["CORR"]),header=None)
        except Exception as e:
            frames['corr']=None

        timestamp=kwargs["timestamp"]

        reftime=self.lastActionBefore('config',timestamp)['timestamp']

        ncpath=self.ncfile(reftime)
        
        feed_NC(ncpath,timestamp,**frames).close()

        self._timeline_add(timestamp)

        return kwargs


    def cleanFeed(self, timestamp):
        reftime=self.lastActionBefore('config',timestamp)['timestamp']
        clean_feed_NC(self.ncfile(reftime), timestamp)
        self.cleanFeatureCache()
        self._timeline_remove(timestamp)

    def updateFeed(self, **kwargs):
        self.cleanFeatureCache()
        return self.feed(**kwargs)


    def data( self, times=None, timeref=None, geometry=None, output="D", **kwargs ):

        #1 Selezionare i file per estrarre i dati in base ai tempi 
        #2 Selezionare il delta di riferimento

        #ATTENZIONE ATTENZIONE!!! FUNZIONA CON UN SOLO FILE DI CONFIGURAZIONE!!


        if times is not None:
            if isinstance(times,slice):
                timefrom=times.start
                timeto=times.stop
            else:
                timefrom=times
                timeto=times
        else:
            timefrom=None
            timeto=None

        conf=self.lastActionBefore('config',timefrom)
        
        reftime=conf['timestamp']
        
        try:
            threshold=conf['ccthreshold']
        except Exception as e:
            threshold=0

        dest_epsg=conf['meta']['crs']

        #COMPORTAMENTO NORMALE
        geometry = transform_geom('EPSG:4326',dest_epsg, geometry)

        geographic = self.getFeatureInfo('map')['geographic']

        targetfile=self.ncfile(reftime)

        data=extract_data(targetfile,geometry=geometry,times=times,output=output,timeref=timeref,geographic=geographic)

        return data


    def map( self, times=None, timeref=None, geometry=None, output="D", cmap=None, **kwargs ):

        timestamp=None

        if isinstance(times,slice):
            timestamp=times.stop
        else:
            timestamp=times


        conf=self.lastActionBefore('config',timestamp)

        mapname=self.hasher(conf['timestamp'])

        if timeref is None:
            reffieldinfile=mapname
        else:
            reffieldinfile=self.hasher(timeref)

        mapmanager= Multiraster(self.uid,mapname)

        ncfile=self.ncfile(mapname)

        mapfile=mapmanager.mapfile

        #conf=conf['value']

        h=conf['meta']['height']
        w=conf['meta']['width']

        if not output in ["CH"]:
            wsc=int(conf['window_size']) 
        else:
            wsc = 0

        timestamp,imgarray=generate_map(
                ncfile,
                timestamp=timestamp,
                timeref=timeref,
                param=output,
                step_size=conf['step_size'],
                threshold=conf['ccthreshold'],
                **ColorMap.parse_colormap(cmap),
                alphacolor=(0,0,0)
                )

        imgname=f"{reffieldinfile}_{self.hasher(timestamp)[:14]}_{output}.tif"

        path_image = mapmanager.mapcache / imgname

        conf['meta']['count']=count=4
        conf['meta']['compress']='LZW'
        conf['meta']['driver']='GTiff'
        conf['meta']['dtype']='uint8'

        imgout=zeros([h,w,count],dtype=conf['meta']['dtype'])
    
        hd=min(imgout.shape[0]-wsc,imgarray.shape[0])
        wd=min(imgout.shape[1]-wsc,imgarray.shape[1])
        
        imgout[wsc:hd,wsc:wd,:count]=imgarray[:hd-wsc,:wd-wsc,:count]

        with rasterio.open(path_image, 'w', **conf['meta']) as dst:
            for i in range(0, count):
                dst.write(imgout[:,:,i],i+1)

        url = mapmanager.geturl(imgname)

        ser=Series([url],index=DatetimeIndex([timestamp]))

        return ser

