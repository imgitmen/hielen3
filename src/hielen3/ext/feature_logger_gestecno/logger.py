# coding=utf-8

from hielen3 import conf
from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema
from marshmallow import fields
from pathlib import Path 
from .helper import func_loggers, retrive
import traceback

class ConfigSchema(ActionSchema):
   
    def _self_hints_():

        try:
            serials=list(func_loggers()['name'])
        except Exception as e:
            serials=[]

        return {
                "Logger info": {
                0:["serial", "Logger serial number", False, serials ],
                1:["header", "Logger header if needed", False, ""]
                },
            }

    serial = fields.String(required=False, allow_none=False)
    header = fields.String(required=False, allow_none=True)



class Feature(HFeature):
    '''
    UNIT
    '''
    

    def setup(self,**kwargs):
        pass
    
    def config(self, serial, **kwargs):

        source=str(self.__module__)

        self.parameters.set(
            "current_1",
            cache='active',
            mu='mA',
            modules={"source":source},
            operator=f"source.retrive(serials={serial!r},times=times,columns=5)")

        self.parameters.set(
            "current_2",
            cache='active',
            mu='mA',
            modules={"source":source},
            operator=f"source.retrive(serials={serial!r},times=times,columns=6)")


