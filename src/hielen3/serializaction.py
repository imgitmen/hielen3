#!/usr/bin/env python
# coding=utf-8

from marshmallow import Schema, fields, ValidationError, INCLUDE
from numpy import datetime64, isnat
from hielen3 import conf
from pathlib import Path
import json
from pandas import DataFrame
from numpy import array, sqrt, sum, where, amin, nan, round
from matplotlib.colors import ColorConverter, Normalize, LinearSegmentedColormap 
from abc import ABC, abstractmethod

### MARSHMALLOW FIELDS

class Style(fields.String):
    """
    
    """
    pass


class FTPPath(fields.String):
    """                      
    Local FTP Filepath manager used to identify a file into the system.
    Mainliy usefull for action Schema declaration in hielen3.HielenSource extention
    """                      
    def _deserialize(self,value, attr, data, **kwargs):
        try:

            return Path(value)

        except Exception as e:
            raise ValueError(e)

    


class LocalFile(fields.String):
    """
    Local Filepath manager used to identify a file into the system.
    Mainliy usefull for action Schema declaration in hielen3.HielenSource extention
    """
    pass

class LoggerHeader(fields.List):
    """
    Logger Header alias
    """

class PolyCoeff(fields.List):
    """
    Polynomial Coefficients list

    intent: 
        giving list a and value x
    result will be

        r=0

        for i in range(0, a._len__()):
            r += a[i]*x**i

    """

    def __init__(self,cls_or_instance=fields.Number,**kwargs):

        super().__init__(cls_or_instance=cls_or_instance,**kwargs)

    def _deserialize(self,value, attr, data, **kwargs):
        try:

            if value in ('null',''):
                return ""

            value=json.loads(value)

            if value is not None:
                value=list(map( lambda x: x is not None and x or 0, value))
                value=",".join(map(str,value))
            
            return value 

        except Exception as e:
            raise e
            raise ValueError(e)

'''
class LoggerHeader(fields.List):
    """
    Logger Header manager
    """

    def __init__(self,cls_or_instance=fields.Tuple(
        (
            fields.String(),    #Param
            fields.Integer(),   #Column
            fields.String(),    #Raw_mu
            fields.String(),    #Ing_mu
            fields.String(),    #Signal_cond
            fields.List(fields.Number()) #Poly coeff
            )
        ),**kwargs):

        super().__init__(cls_or_instance=cls_or_instance,**kwargs)

    def _deserialize(self,value, attr, data, **kwargs):
        try:

            return json.loads(value)

        except Exception as e:
            raise ValueError(e)
'''

class ParamsDefinition(fields.List):
    """
    Logger Header manager
    """

    def __init__(self,cls_or_instance=fields.Tuple(
        (
            fields.String(),    #Param
            fields.Integer(),   #Column
            fields.String()    #Ing_mu
            )
        ),**kwargs):

        super().__init__(cls_or_instance=cls_or_instance,**kwargs)

    def _deserialize(self,value, attr, data, **kwargs):
        try:

            return json.loads(value)

        except Exception as e:
            raise ValueError(e)


class ColorMap(fields.List):
    """
    Colormap manager used to identify a colormap
    """

    def __init__(self,cls_or_instance=fields.Tuple((fields.String(),fields.Number())),**kwargs):
        super().__init__(cls_or_instance=cls_or_instance,**kwargs)

    def _deserialize(self,value, attr, data, **kwargs):
        try:

            return ColorMap.make_colormap(json.loads(value))

        except Exception as e:

            try:
                assert value['f_cmap']
                return value
            except Exception as e:
                raise ValueError(e)

    def valorizeColor(clmap,color):

        c = ColorConverter()

        try:
            colframe=DataFrame([c.to_rgb(x[1]) for x in clmap])
        except ValueError as e:
            colframe=DataFrame([x[1] for x in clmap])
            colframe=colframe/255
            colframe=colframe.apply(c.to_rgb,axis=1,result_type='expand')

        colframe.columns=['r','g','b']

        colframe['values'] = [x[0] for x in clmap]

        colors=colframe[['r','g','b']].values

        colframe=colframe.set_index(['r','g','b'])

        color=array(color)
        try:
            color=array(c.to_rgb(color))
        except ValueError as e:
            color=DataFrame([color],columns=['r','g','b'])/255
            color=color.apply(c.to_rgb,axis=1,result_type='expand').values

        distances = sqrt(sum((colors-color)**2,axis=1))

        index_of_smallest = where(distances==amin(distances))

        try:
            return float(colframe['values'].iloc[index_of_smallest].squeeze())
        except Exception as e:
            return nan



    def parse_colormap(incmap):
    
        if incmap is None:
            return ColorMap.parse_colormap(ColorMap.make_colormap())

        try:
            norm=Normalize(**incmap["norm"])
            norm.clip=True
        except Exception:
            norm = None

        cmap=LinearSegmentedColormap('CustomMap', incmap['b_cmap'])

        return { "norm":norm, "cmap":cmap}

    def make_colormap(incmap=None):

        if incmap is None:
            incmap=[[-0.25,"#FF0000"],[0,"#00FF00"],[0.25,"#0000FF"]]

        a=DataFrame(incmap,columns=["values","colors"]).sort_values("values")
        out={"norm":{"vmin":a["values"][0],"vmax":a["values"].iloc[a.shape[0]-1]}}
        n=Normalize(**out["norm"])
        a["values"]=round(a["values"],3)
        a["idx"]=n(a["values"])*100
        cc=a[["idx","colors"]].values
        seq=[]
        c = ColorConverter()

        for i in range(cc.__len__()):
            if i == 0 or i == cc.__len__():
                seq.append(c.to_rgb(cc[i][1]))
            else:
                seq.append(c.to_rgb(cc[i][1]))
                seq.append(cc[i][0]/100)
                seq.append(c.to_rgb(cc[i][1]))
                
        seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]

        linsegcmap = {'red': [], 'green': [], 'blue': []}
        for i, item in enumerate(seq):
            if isinstance(item, float):
                r1, g1, b1 = seq[i - 1]
                r2, g2, b2 = seq[i + 1]
                linsegcmap['red'].append([item, r1, r2])
                linsegcmap['green'].append([item, g1, g2])
                linsegcmap['blue'].append([item, b1, b2])

        out["f_cmap"]=a.values.tolist()
        out["b_cmap"]=linsegcmap
	
        return out



class StringTime(fields.DateTime):
    
    def _agoodtime(t):

        try:
            t=datetime64(t)
            assert not isnat(t)
            t=str(t)
        except Exception as e:
            t=None
        return t


    def _deserialize(self, value, attr, data, **kwargs):
        return str(super()._deserialize(value, attr, data, **kwargs))

    def _serialize(self, value, attr, obj, **kwargs):
        return StringTime._agoodtime(value)


class HSchema(Schema):
    '''
    Minimal ancestor class providing mehods
    '''

    class Meta:
        unknown = INCLUDE


    @property
    def __hdict__(self):
        out = { "fields":{},"required":[], "hints":self.hints }
        for k,w in self.dump_fields.items():
            out['fields'][k]=w.__class__.__name__
            w.__dict__['required'] and out["required"].append(k)

        return out

    @abstractmethod
    def _self_hints_():
        pass

    @property
    def hints(self):
        out = self.__class__._self_hints_() or {}
        for c in self.__class__.__bases__:
            try:
                out.update(c().hints)
            except AttributeError as e:
                print ("ATTRIBUTE ERROR:," c, e)
            except TypeError as e:
                print ("TYPE ERROR:", c, e)

        return out

    timestamp = StringTime(required=True, allow_none=False)



class ActionSchema(HSchema):
    '''
    Minimal ActionSchema object. Used to define at least a timestamp
    '''

    def _self_hints_():
        return {
            "Base": {
                0: ["timestamp","Reference time" , False, None ]
                }
            }

    timestamp = StringTime(required=True, allow_none=False)

"""
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
"""




