#!/usr/bin/env python
# coding=utf-8
import mappyfile
import re
from hielen3 import conf
from abc import ABC, abstractmethod
from pathlib import Path
from hielen3.sourcestorage import SourceStorage

class Mapmanager(ABC):

    def __init__(self,feature,mapname,*args,**kwargs):
        subpath = Path(feature) / mapname
        self.mapbaseurl=Path( conf['mapurl'] ) / subpath
        self.mapcache = SourceStorage(conf['syscache']['mapcache'], str(subpath))

    @property
    def mapfile(self):
        return self.mapcache / "mapfile.map"


    @property
    def mapurl(self):
        return self.mapbaseurl / "mapfile.map"


    @abstractmethod
    def setMFparams():
        pass

    @abstractmethod
    def geturl():
        pass


class Multiraster(Mapmanager):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.maptype='multiraster'

    def setMFparams(
            self,
            bands=4, 
            scale=['0,255','0,255','0,255','0,255'], 
            crs='EPSG:3857', 
            lyrext='-20026376.39 -20048966.10 20026376.39 20048966.10',
            datadir='', 
            um='METERS',
            ows_onlineresources="http://pippo&"
            ):


        inmapf=conf['maptemplates'][self.maptype]
        self.mapcache.mkdir()
        mapfile = mappyfile.open(inmapf)
        mapfile["shapepath"] = datadir
        mapfile["web"]["metadata"]["ows_onlineresource"] = ows_onlineresources

        if ( bands == 1 ):
            scale=['0,65536']

        layer = mapfile["layers"][0]

        tbands=','.join(map(str,(range(1,bands+1))))
        layer['processing']=[f'BANDS={tbands}']

        for i in range (0,bands):
            layer['processing'].append(f"SCALE_{i+1}={scale[i]}")

        layer["projection"] = f"init={str(crs).lower()}"

        try:
            um = um.upper()
        except Exception as e:
            pass

        if um is None or not um or um in ['UNKNOWN']:
            um = "METERS"

        layer["units"] = re.sub('METRES?','METERS',um.upper())

        layer["metadata"]["ows_srs"] = str(crs).upper()

        layer["metadata"]["ows_extent"] = lyrext

        #layer["composite"]["opacity"] = opacity

        mappyfile.save(mapfile, self.mapfile, 2)




    def geturl(self,imgname):


        url=[
                str(self.mapbaseurl),
                "?SERVICE=WMS&VERSION=1.1.1",
                "&imgfile="+ str(imgname),
                "&layers=imglyr",
                "&transparent=true",
                "&format=image/png",
                "&mode=tile",
                "&tilemode=gmap",
                "&tile={x}+{y}+{z}",
                ]

        #return urllib.parse.quote("".join(url))
        return "".join(url)

