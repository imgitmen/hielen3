#!/usr/bin/env python
# coding=utf-8
from pathlib import Path, os
from shutil import rmtree

import traceback

class SourceStorage():

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.cache)

    def __init__(self, syspath, subpath=''):
        self.cache=Path(syspath) / subpath

    def __truediv__(self, other):
        other = str(other).replace(f"{self.cache}{os.sep}","")
        return self.cache / other

    def glob(self,*args,**kwargs):
        return self.cache.glob(*args,**kwargs)

    def mkdir(self,path=None):
        if path is None: path = ''
        outpath = self / path
        os.makedirs( outpath , exist_ok=True)
        return outpath

    def rmdir(self,path=None):

        if path is None: path = ''
        outpath = self.cache / path
        rmtree(outpath)

