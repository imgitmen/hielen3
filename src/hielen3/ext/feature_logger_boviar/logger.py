# coding=utf-8

from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema, LocalFile
from marshmallow import fields
from pandas import read_excel
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
                1:["header", "Logger header xlsx", False, ""]
                },
            }

    serial = fields.String(required=False, allow_none=False)
    header = LocalFile(required=True, allow_none=False)



class Feature(HFeature):
    

    def setup(self,**kwargs):
        pass


    def setpar(self,module,serial,name,unit):
         self.parameters.set(
            name,
            cache='active',
            mu=unit,
            modules={"source":module},
            operator=f"source.retrive(serials={serial!r},times=times,columns={name!r})")


    
    def config(self, serial, header, **kwargs):

        module=str(self.__module__)

        header=read_excel(header,header=None,index_col=0)

        header.apply(lambda x: self.setpar(*[module,serial,*x]))


