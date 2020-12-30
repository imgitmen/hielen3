# coding=utf-8

from hielen2.datalink import HielenSource
from hielen2.utils import LocalFile
import rasterio
#from . import ncmangle 
from marshmallow import Schema, fields

class ConfigSchema(Schema):
    timestamp = fields.Str(required=True, allow_none=False)
    master_image = LocalFile(required=True, allow_none=False)
    step_size = fields.Str(required=False, default="8")
    window_size_change = fields.Str(required=False,default="0")
    world_file = LocalFile(required=False,default=None)
    crs=fields.Str(required=False,default="EPSG:3857")


class Source(HielenSource):

    def _get_im_info(impath):
        return {}

    def _get_wf_info(wfpath):
        return {}

    def config(self, **kwargs):

        out={}

        img=rasterio.open(kwargs["master_image"])
        out['timestamp']=kwargs['timestamp']
        out['step_size']=kwargs['step_size']
        out['window_size_change']=kwargs['window_size_change']
        out['affine']=[1,0,0,0,1,0]
        out['crs']=kwargs['crs']

        try:
            out['crs']=img.crs.data['init']
        except Exception as e:
            pass

        try:
            with open(kwargs["world_file"]) as f:
                wfv=f.read().split("\n")[0:6]
                ATM=[wfv[0],wfv[2],wfv[4],wfv[1],wfv[3],wfv[5]]
        except Exception as e:
            pass

        print (self.__dict__)

        return self.actions['config']

    def feed(self, **kwargs):
        return kwargs

    def data(self, timefrom=None, timeto=None, geom=None, **kwargs):
        return kwargs
