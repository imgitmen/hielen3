# coding=utf-8

__name__ = "Feature_logger_gestecno"
__version__ = "0.0.1"
__author__ = "Alessandro Modesti"
__email__ = "it@img-srl.com"
__description__ = "HielenSource extensione"
__license__ = "MIT"
__uri__ = ""


from marshmallow import fields
from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DatetimeIndex, DataFrame 
from hielen3.serializaction import ActionSchema
from .logger import Feature

folders=[
        {
            'type':'gestecno',
            'path':'gestecno_rfi/data'
            }, 
        {
            'type':'gestecno',
            'path':'gestecno_saa/diag'
            }
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        a=read_csv(path,skiprows=2,parse_dates=True,header=None)
        if a.empty:
            a = read_csv(path,parse_dates=True,header=None)
            a = a[a[0].apply(lambda x: match('^\d{4}-\d{2}',x)).notna()]

        a.columns = [ 'times', *a.columns[1:] ]
    
    except Exception as e:
        #raise e
        pass

    return a


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
    header = fields.String(required=False, allow_none=False)


__all__ = ["Feature", "ConfigSchema", "retriver", "func_loggers" ]

