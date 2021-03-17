# coding=utf-8

from hielen2.source import HielenSource, ActionSchema, StringTime, sourceFactory
from hielen2.utils import LocalFile
from hielen2.maps.mapper import setMFparams 
import rasterio
import magic
import os
import re
from pathlib import Path
from .struct import config_NC, feed_NC, generate_map
from marshmallow import fields
from shutil import rmtree
from numpy import arange, full, zeros
from pandas import read_csv, DataFrame, Series, DatetimeIndex
import traceback

class ConfigSchema(ActionSchema):
    """'master_image' (required): the base image used as reference grid for elaboration. It can be any \
image format managed by rasterio pyhton library (GeoTIFF, jpeg, ...). Any elaboration image based \
on the 'master_image' will share geometry and reference system with it.

'step_size': Pixels sub samplig ratio expected for the elaboration grids compared to 'master_image'. \
(see Feed Action)

'windows_size_change': Pixel expressed, upper-left corner position (both vertical and orizontal) expected \
for the overlaying elaboration grids starting from the upper-left corner of the 'master_image'

'geo_reference_file': Reference file for the geolocalization of the 'master_image' and all the dependent \
elaboration images. It can be a standard world file (six lines text file) according to \
http://www.kralidis.ca/gis/worldfile.htm, as well an '.aux.xml' file according to \
https://desktop.arcgis.com/en/arcmap/10.3/manage-data/raster-and-images/auxiliary-files.htm \
(just the Coordinate system, the Transformation and the Projection informations are here managed).
IMPORTANT: When a valid 'geo_regerence_file' is provided, therein informations overwrite the ones \
possibly embedded into the 'master_image'

'crs': the Coordinate Reference System of the master_image in the string form 'autority:code' \
(i.e.: 'EPSG:3857'). 
IMPORTANT: If a valid 'crs' is provided, this value overwrites the ones possibly provided with the \
'geo_regerence_file' and/or embeded into the 'master_image'
"""
    master_image = LocalFile(required=True, allow_none=False)
    step_size = fields.Number(required=False, default=1, allow_none=True, as_string=False)
    window_size_change = fields.Number(required=False,default=0, allow_none=True, as_string=False)
    geo_reference_file = LocalFile(required=False,default=None, allow_none=True)
    crs=fields.Str(required=False,default=None,allow_none=True)


class FeedSchema(ActionSchema):
    """reference_time: timestamp of the reference "master_image". If Null assumes last \
"master_image" configured.

NS_displacement: textfile containing the grid of the North-South displacement.

EW_displacement: textfile containing the grid of the East-Weast displacement.

CORR: textfile containing the grid of the coerence info
"""

    NS_displacement = LocalFile(required=True, allow_none=False)    
    EW_displacement = LocalFile(required=True, allow_none=False)    
    CORR = LocalFile(required=False, allow_none=True)    


class Source(HielenSource):
    '''
    PhotoMonitoring source manager
    '''

    def hasher(self,*args,**kwargs):
        h=[ *args ]
        h.extend(list(kwargs.values()))
        h=''.join([ str(a) for a in h])
        return re.sub("[^\d]","",h)[0:14]

    def config_last_before(self,timestamp):
        c=self.getActionValues('config',slice(None,timestamp))
        try:
            return c[-1]
        except Exception as e:
            return None

    def ncfile_path(self,timestamp):
        return self.filecache / f"{self.hasher(timestamp)}.nc"

    def masterimg_path(self,timestamp):
        return self.mapcache / f"{self.hasher(timestamp)}.tiff"

    def mapfile_path(self,timestamp):
        return self.mapcache / f"{self.hasher(timestamp)}.map"

    def config(self, **kwargs):

        out={}

        timestamp=kwargs['timestamp']

        #Temporary image path
        path_temp_image=Path(kwargs["master_image"])
        
        self.filecache.mkdir()
        self.mapcache.mkdir()

        path_masterimg=self.masterimg_path(timestamp)
        path_mapfile=self.mapfile_path(timestamp)
        path_geo_ref=None

        try:
            name=str(path_temp_image).split(".")

            #Temporary georef file
            path_temp_ref=Path(kwargs["geo_reference_file"])

            with open(path_temp_ref) as trf:
                '''
                trying to match reference file type (wld or aux.wml) if exists
                '''
                try:
                    float(trf.readline())
                    path_geo_ref=Path(".".join([*name[0:-1],"wld"]))
                except Exception as e:
                    path_geo_ref=Path(".".join([*name,"aux","xml"]))

            path_temp_ref.replace(path_geo_ref)

        except Exception as e:
            pass
            # traceback.print_exc()

        try:
            '''
            trying to define crs from income parameters
            '''
            crs=rasterio.crs.CRS.from_string(kwargs['crs'])
        except Exception:
            crs=None

        try:
            with rasterio.open(path_temp_image) as src:
                meta = src.meta.copy()
                if crs is not None:
                    meta['crs']=crs

                meta['transform']=list(meta['transform'])[0:6]

                try:
                    meta['crs']=meta['crs'].to_string()
                except AttributeError:
                    meta['crs']=None

                meta['count']=3
                meta['compress']='lzw'
                meta['dtype']='uint8'

                    
                if src.count == 1:
                    #trasformare da gray scale a rgb
                    rgb = src.read(1).copy()
                    rgb = (rgb/2**16)*255
                    rgb = rgb.astype('uint8')
                    rgb = [rgb,rgb,rgb]
                else:
                    rgb = src.read()

                with rasterio.open(path_masterimg, 'w', **meta) as dst:
                    for i in range(0, rgb.__len__()):
                        dst.write(rgb[i],i+1)

                bands=dst.meta['count']
                outcrs=dst.meta['crs']
                outum=outcrs.linear_units

                #Master_image is ok. Macking mapfile
                setMFparams(path_mapfile, bands=bands, crs=outcrs, um=outum)

        except Exception as e:
            raise ValueError(e)

                    

        x_offset=y_offset=kwargs['window_size_change'] or 0
        step_size=kwargs['step_size'] or 1

        out['master_image']=magic.from_file(str(path_masterimg))
        out['timestamp']=timestamp
        out['step_size']=step_size
        out['window_size_change']=x_offset
        out['meta']=meta

        x_values=arange(y_offset,meta['width'],step_size)*meta['transform'][0]+meta['transform'][2]
        y_values=arange(x_offset,meta['height'],step_size)*meta['transform'][4]+meta['transform'][5]

        ncpath=self.ncfile_path(timestamp)

        config_NC(ncpath,timestamp,x_values,y_values).close()

        return out 

    def cleanConfig(self,timestamp):

        os.unlink(self.ncfile_path(timestamp))
        os.unlink(self.masterimg_path(timestamp))
        os.unlink(self.mapfile_path(timestamp))


    def feed(self, **kwargs):

        fileNS=Path(kwargs["NS_displacement"])
        fileEW=Path(kwargs["EW_displacement"])

        try:
            fileCORR=Path(kwargs["CORR"])
        except Exception as e:
            fileCORR=None

        timestamp=kwargs["timestamp"]
        reftime=self.config_last_before(timestamp)['timestamp']

        ncpath=self.ncfile_path(reftime)
        
        frames={"ns":None,"ew":None,"corr":None}

        frames["ns"] = read_csv(fileNS,header=None)

        frames["ew"] = read_csv(fileEW,header=None)
    
        if fileCORR is None:
            frames["corr"] = DataFrame(full((frames["ns"].shape),0.99))
        else:
            frames["corr"] = read_csv(fileCORR,header=None)

        feed_NC(ncpath,timestamp,**frames).close()

        return kwargs

    def cleanFeed(timestamp):
        pass

    def data(feat, timefrom=None, timeto=None, geom=None, **kwargs):
        return kwargs


def map( feature, times=None, timeref=None, output="RV" ):

    feature = sourceFactory(feature)

    timestamp=None

    if isinstance(times,slice):
        timestamp=times.stop
    else:
        timestamp=times
    
    conf=feature.config_last_before(timestamp)

    reftimestamp=timeref or conf['timestamp']

    ncfile=feature.ncfile_path(conf['timestamp'])
    mapfile=feature.mapfile_path(conf['timestamp'])

    conf=conf['value']

    h=conf['meta']['height']
    w=conf['meta']['width']
    wsc=int(conf['window_size_change'])

    imgout=zeros([h,w,4])
    timestamp,imagearray=generate_map(ncfile,timestamp=timestamp,timeref=timeref,param=output,step_size=conf['step_size'])
    imgout[wsc:,wsc:]=imagearray[:h-wsc,:w-wsc]

    imgname=f"{feature.hasher(timestamp)}_{feature.hasher(reftimestamp)}_{output}.tiff"
    path_image=feature.mapcache / imgname

    conf['meta']['count']=3
    conf['meta']['compress']='LZW'
    conf['meta']['driver']='GTiff'
    conf['meta']['dtype']='uint8'

    imagearray=imagearray[:h-wsc,:w-wsc,0:conf['meta']['count']]

    with rasterio.open(path_image, 'w', **conf['meta']) as dst:
        for i in range(0, conf['meta']['count']):
            dst.write(imagearray[:,:,i],i+1)

    url=[ 
            "http://localhost:8081/maps/mapserv",
            "?map="+ str(mapfile),
            "&SERVICE=WMS&VERSION=1.1.1",
            "&imgfile="+ str(imgname),
            "&layers=imglyr",
            "&transparent=true",
            "&format=image/png",
            "&mode=tile",
            "&tilemode=gmap",
            "&tile=364+214+10",

        ]

    url="".join(url)

    ser=Series([url],index=DatetimeIndex([timestamp]))

    return ser




