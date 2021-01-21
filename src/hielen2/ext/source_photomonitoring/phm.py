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


class ConfigSchema(ActionSchema):
    master_image = LocalFile(required=True, allow_none=False)
    step_size = fields.Str(required=False, default="8")
    window_size_change = fields.Str(required=False,default="0")
    geo_reference_file = LocalFile(required=False,default=None)
    crs=fields.Str(required=False,default=None)


class FeedSchema(ActionSchema):
    reference_time = fields.DateTime(required=False, allow_none=False)
    NS_displacement = LocalFile(required=False, allow_none=False)    
    EW_displacement = LocalFile(required=False, allow_none=False)    
    Coer = LocalFile(required=False, allow_none=False)    


class Source(HielenSource):
    '''
    def __init__(self, feature, filecache):
        self.__dict__.update(feature.pop('properties'))
        self.geometry=feature.pop('geometry')
        self.actions=feature
        self.filecache = os.path.join(filecache,self.uid)
        os.makedirs(self.filecache, exist_ok=True)
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
                
                try:
                    float(trf.readline())
                    path_georef=Path(".".join([*name[0:-1],"wld"]))
                except Exception as e:
                    path_georef=Path(".".join([*name,"aux","xml"]))

            Path(path_tempref).replace(path_georef)

        except Exception as e:
            pass

        try:
            crs=rasterio.crs.CRS.from_string(kwargs['crs'])
        except Exception:
            crs=None

        with rasterio.open(path_tempimage) as src:
            meta = src.meta.copy()
            if crs is not None:
                meta.update({'crs': crs })

            with rasterio.open(path_masterimage, 'w', **meta) as dst:
                for i in range(1, src.count + 1):
                    dst.write(src.read(i),i)

                    
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


    def feed(self, **kwargs):
        return kwargs

    def data(self, timefrom=None, timeto=None, geom=None, **kwargs):
        return kwargs
