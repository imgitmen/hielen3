#!/usr/bin/env python
# coding=utf-8
from hielen3 import conf
from abc import ABC, abstractmethod
from pathlib import Path, os
from hielen3.sourcestorage import SourceStorage
from glob import glob
import re
import json

class Cloudmanager(ABC):

    def __init__(self,feature,basepath,*args,**kwargs):
        basepath = Path(feature) / basepath
        self.cloudbaseurl=Path( conf['cloudurl'] ) / 'viewer.html'
        self.cloudcache = SourceStorage(conf['syscache']['cloudcache'], str(basepath))
        self.basepath=basepath

    """
    @property
    def mapfile(self):
        return self.mapcache / "mapfile.map"


    @property
    def mapurl(self):
        return self.mapbaseurl / "mapfile.map"


    @abstractmethod
    def setMFparams():
        pass
    """



    @abstractmethod
    def geturl():
        pass


class PotreeCM(Cloudmanager):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def makePotree(self,lazfile,cloudname, subpath=None):

        targhetpath=self.cloudcache / ( subpath or "") / cloudname

        return os.system(f"{conf['potreeconverter']} {lazfile} -o {targhetpath}")



    def geturl(self,subpath,cloud=None):

        if cloud is None:
            cloud="*"

        sub = self.cloudcache / subpath

        clouds=[]
        clswitch={}

        #basepath = self.cloudcache / 'base' / 'metadata.json'

        #metto la base se esiste
        #if basepath.exists():
        #    clouds['base']=str(basepath).replace(conf['syscache']['cloudcache'],"resources")
        
        on=1
    
        for p in self.cloudcache.glob('*'):
            if p.is_dir() and (p / 'metadata.json').exists():
                relpath=str(p/'metadata.json').replace(conf['syscache']['cloudcache'],"resources")
                clouds.append({"name":p.name,"path":relpath,"switch":on})
                on = 0

        on=1
        #cerco le altre clouds
        for p in sub.glob(cloud):
            if p.is_dir() and (p / 'metadata.json').exists():
                relpath=str(p/'metadata.json').replace(conf['syscache']['cloudcache'],"resources")
                clouds.append({"name":p.name,"path":relpath,"switch":on})
                on = 0

        url=str(self.cloudbaseurl)+"?clouds="+ json.dumps(clouds)

        return url

