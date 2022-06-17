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

        header={
                1:{ "name": "battery", "mu":"V", "ordinal":1},
                2:{ "name": "temp", "mu":"°C", "ordinal": 2},
                4:{ "name": "CE01_ch_A", "mu": "mA", "ordinal": 3},
                5:{ "name": "CE01_ch_B", "mu": "mA", "ordinal": 4},
                6:{ "name": "CE01_temp", "mu": "°C", "ordinal": 5},
                7:{ "name": "CE02_ch_A", "mu": "mA", "ordinal": 6},
                8:{ "name": "CE02_ch_B", "mu": "mA", "ordinal": 7},
                9:{ "name": "CE02_temp", "mu": "°C", "ordinal": 8},
                10:{ "name": "CE03_ch_A", "mu": "mA", "ordinal": 9},
                11:{ "name": "CE03_ch_B", "mu": "mA", "ordinal": 10},
                12:{ "name": "CE03_temp", "mu": "°C", "ordinal": 11},
                13:{ "name": "CE04_ch_A", "mu": "mA", "ordinal": 12},
                14:{ "name": "CE04_ch_B", "mu": "mA", "ordinal": 13},
                15:{ "name": "CE04_temp", "mu": "°C", "ordinal": 14}
            }


        source=str(self.__module__)

        for k,w in header.items():
            self.parameters.set(
                w["name"],
                cache='active',
                mu=w['mu'],
                ordinal=w['ordinal'],
                modules={"source":source},
                operator=f"source.retrive(serials={serial!r},times=times,columns={k})")


