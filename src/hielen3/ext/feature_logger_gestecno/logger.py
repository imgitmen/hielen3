# coding=utf-8

from hielen3 import conf
from hielen3.feature import HFeature
from hielen3.series import HSeries
from hielen3.serializaction import ActionSchema, FTPPath, PolyCoeff, LoggerHeader
from marshmallow import fields
from pathlib import Path 
import traceback



class Feature(HFeature):
    '''
    UNIT
    '''
    

    def setup(self,**kwargs):
        pass
    
    def config(self, serial, piezo_1=None, piezo_2=None, **kwargs):

        source=str(self.__module__)

        if not self.parameters.__len__():
            if piezo_1 is None: piezo_1=""
            if piezo_2 is None: piezo_2=""

        self.parameters.set(
            "current_1",
            cache='active',
            mu='°mA',
            modules={"source":source},
            operator=f"source.retrive(serials={serial!r},times=times,columns=5)")

        self.parameters.set(
            "current_2",
            cache='active',
            mu='°mA',
            modules={"source":source},
            operator=f"source.retrive(serials={serial!r},times=times,columns=6)")

        if piezo_1 is not None:
            self.parameters.set(
                    'water_higth_2',
                    cache='active',
                    mu="m",
                    modules={"calc":"hielen3.tools.calc"}, 
                    operands={"S0":self.parameters["current 1"].uuid},
                    operator=f"calc.poly_trans2(S0,{piezo_1})")

        if piezo_2 is not None:
            self.parameters.set(
                    'water_higth_2',
                    cache='active',
                    mu="m",
                    modules={"calc":"hielen3.tools.calc"}, 
                    operands={"S0":self.parameters["current 2"].uuid},
                    operator=f"calc.poly_trans2(S0,{piezo_2})")



