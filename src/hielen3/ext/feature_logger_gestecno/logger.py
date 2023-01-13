# coding=utf-8

from hielen3 import conf
from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema
from marshmallow import fields
from pathlib import Path 
from .helper import func_loggers, retrive
import json
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
    
    def config(self, timestamp, serial, header=None,**kwargs):

        """
        header=
        [
            {
                "channel": "nomechannel1",
                "mu": "measurement_unit1",
                "column" : #1,
                "valid_range" : [start,end]
            },
            {
                "channel": "nomechannel2",
                "mu": "measurement_unit2",
                "column" : #2,
                "valid_range" : [start,end]
            },

            ...
            
            {
                "channel": "nomechannelN",
                "mu": "measurement_unitN",
                "column" : #N,
                "valid_range" : [start,end]
            }

        ]

            

        """

        source=str(self.__module__)

        if header is None:
            header={}

        try:
            infos=json.loads(header)
        except Exception as e:
            raise e

        for info in infos:
            self.parameters.set(
                    param=info['channel'],
                    ordinal=info['column'],
                    cache=info['cache'],
                    mu=info['mu'],
                    modules={"source":source},
                    operands={ "SER": serial, "COL":info["column"] },
                    operator=f"source.retrive(serials=SER,times=times,columns=COL)",
                    valid_range=info['valid_range'],
                    view_range=None,
                    thresholds=None
                    )




        """
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
        """


