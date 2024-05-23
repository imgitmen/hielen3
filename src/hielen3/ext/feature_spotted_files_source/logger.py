# coding=utf-8

from hielen3 import conf
from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema
from marshmallow import fields
from pathlib import Path 
from pandas import read_excel, DataFrame
from datetime import datetime
import json
import traceback

class ConfigSchema(ActionSchema):
   
    def _self_hints_():

        try:
            serials=list(func_loggers()['name'])
        except Exception as e:
            serials=[]

        return {
                "file info": {
                    0:["serial", "source file under incomes MANUAL (called 'serial' for compatibilities)", False, None],
                    1:["header", "source file header if needed", False, ""]
                }
            }

    serial = fields.String(required=False, allow_none=False)
    header = fields.String(required=False, allow_none=True)



class Feature(HFeature):
    '''
    UNIT
    '''

    def setup(self,**kwargs):
        #self.update(intent="HIDDEN")
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

        #### NOTA!!!!!!!!!!!!
        """
        serial è il percorso path del file. Chiamato serial per compatibilità
        """

        path= str(Path(conf['incomepath']) / "manuali" / serial )

        for info in infos:

            template={ 
                    "channel": None,
                    "mu": None,
                    "column": None ,
                    "cache": "old",
                    "valid_range": None 
                    }

            template.update(info)

            if template["channel"] is None:
                template["channel"] = template["column"]

            info=template

            self.parameters.set(
                    param=info['channel'],
                    ordinal=info['column'],
                    cache=info['cache'],
                    mu=info['mu'],
                    modules={"source":source},
                    operands={ "PATH": path, "COL": info["column"] },
                    operator=f"source.retrive(path=PATH,times=times,columns=COL)",
                    valid_range=info['valid_range'],
                    view_range=None,
                    thresholds=None
                    )

def retrive(path, times=None, columns=None):

    a=DataFrame([],dtype='object')

    if columns is None:
        columns = slice(None,None)

    if isinstance(columns,str):
        columns=[columns]

    if isinstance(times,(datetime,str)):
        times=str(times)

    if times is None or not isinstance(times,slice):
        times=slice(times,None,None)

    try:
        a=read_excel(path,parse_dates=[0])
        a.columns = [ 'times', *a.columns[1:] ]
    except Exception as e:
        print("WARN : ", e, path)
        pass

    a=a.set_index('times')

    return a.loc[times,columns]

