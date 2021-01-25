# coding=utf-8

from hielen2.source import HielenSource, ActionSchema
from hielen2.utils import LocalFile
import rasterio
import magic
import os
import re
from pathlib import Path
from .ncmangle import NCMangler
from marshmallow import fields
from shutil import rmtree


class ConfigSchema(ActionSchema):
    """'master_image' (required): the base image used as reference grid for elaboration. I can be any \
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

'crs': the Coordinate reference system of the master_image in the string form 'autority:code' \
(i.e.: 'EPSG:3857'). 
IMPORTANT: If a valid 'crs' is provided, this value overwrites the ones possibly provided with the \
'geo_regerence_file' and/or embeded into the 'master_image'
"""
    master_image = LocalFile(required=True, allow_none=False)
    step_size = fields.Str(required=False, default="8")
    window_size_change = fields.Str(required=False,default="0")
    geo_reference_file = LocalFile(required=False,default=None)
    crs=fields.Str(required=False,default=None)


class FeedSchema(ActionSchema):
    """reference_time: timestamp of the reference "master_image". If Null assumes last \
"master_image" configured.

NS_displacement: textfile containing the grid of the North-South displacement.

EW_displacement: textfile containing the grid of the East-Weast displacement.

Coer: textfile containing the grid of the coerence info
"""

    reference_time = fields.DateTime(required=False, allow_none=False)
    NS_displacement = LocalFile(required=False, allow_none=False)    
    EW_displacement = LocalFile(required=False, allow_none=False)    
    Coer = LocalFile(required=False, allow_none=False)    


class Source(HielenSource):
    '''
    PhotoMonitoring source manager
    '''


    def config(self, **kwargs):

        out={}

        path_tempimage=Path(kwargs["master_image"])
        path_tempref=kwargs["geo_reference_file"]
        
        refpath=self.makeCachePath( re.sub("[^\d]","",kwargs['timestamp']) )
        path_masterimage=Path(refpath) / "master.img"
        path_masternetcdf=Path(refpath) / "master.nc"
        path_georef=None


        try:
            name=str(path_tempimage).split(".")

            with open(path_tempref) as trf:
                '''
                trying to match reference file type (wld or aux.wml) if exists
                '''
                try:
                    float(trf.readline())
                    path_georef=Path(".".join([*name[0:-1],"wld"]))
                except Exception as e:
                    path_georef=Path(".".join([*name,"aux","xml"]))

            Path(path_tempref).replace(path_georef)

        except Exception as e:
            pass

        try:
            '''
            trying to define crs from 
            '''
            crs=rasterio.crs.CRS.from_string(kwargs['crs'])
        except Exception:
            crs=None

        try:
            with rasterio.open(path_tempimage) as src:
                meta = src.meta.copy()
                if crs is not None:
                    meta.update({'crs': crs })

                with rasterio.open(path_masterimage, 'w', **meta) as dst:
                    for i in range(1, src.count + 1):
                        dst.write(src.read(i),i)
        except Exception as e:
            raise ValueError(e)

                    
        out['master_image']=magic.from_file(str(path_masterimage))
        out['timestamp']=kwargs['timestamp']
        out['step_size']=kwargs['step_size']
        out['window_size_change']=kwargs['window_size_change']
        out['transform']=list(meta['transform'])[0:6]
        out['cache']=self.getRelativePath(refpath)

        try:
            out['crs']=meta['crs'].to_string()
        except AttributeError:
            out['crs']=None

        #nc=NCMangler(path_masternetcdf,**out)

        return out 

    def deleteConfig(self,timestamp):
        p = Path(self.filecache) / Path (re.sub("[^\d]","",timestamp))
        rmtree(p)

    def feed(self, **kwargs):
        return kwargs


    def deleteFeed(timestamp):
        pass


    def data(self, timefrom=None, timeto=None, geom=None, **kwargs):
        return kwargs
