# coding=utf-8

from hielen3 import conf
from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema
from marshmallow import fields
from pathlib import Path 
from pandas import read_csv, DatetimeIndex, Series
#from .helper import func_loggers, retrive
import json
import re
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


        for info_new in infos:

            info=dict(
                    cache='old',
                    valid_range=None,
                    view_range=None,
                    thresholds=None
                    )

            info.update(info_new)

            self.parameters.set(
                    param=info['channel'],
                    ordinal=info['column'],
                    cache=info['cache'],
                    mu=info['mu'],
                    modules={"source":source},
                    operands={ "SER": serial, "COL":info["column"] },
                    operator=f"source.retrive(serials=SER,times=times,columns=COL)",
                    valid_range=info['valid_range'],
                    view_range=info['view_range'],
                    thresholds=info['thresholds']
                    )



def retrive(serials=None,times=None,columns=None):

    loggerpath=Path(conf['incomepath'], 'move', serials, 'last_load.csv' )

    data=read_csv( loggerpath )
    
    data.index=Series(data['timestamp']).astype(str).apply(lambda x: re.sub('.000Z$','', x))

    data.drop('timestamp',axis=1)

    if not isinstance(times, slice):
        times = slice (None,None,None)

    return data[times][columns]



