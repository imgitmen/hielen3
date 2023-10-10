# coding=utf-8

from hielen3 import conf
from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema
from marshmallow import fields
from pathlib import Path 
import json
import traceback
from pandas import DataFrame, Series, to_datetime, concat 
from zeep import Client          
from zeep.helpers import serialize_object 
from concurrent.futures import ThreadPoolExecutor 
from functools import wraps      
from time import time            
from hielen3.utils import isot2ut
from datetime import datetime

'''                              
                                 
sudo apt-get install libxml2-dev libxslt1-dev 
                                 
pip install lxml==4.2.5 zeep     
                                 
'''  


class ConfigSchema(ActionSchema):

    def _self_hints_():
        return {
                "Logger info": {
                0:["serial", "Logger serial number", False, [] ],
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
                "gwserial": "..."
                "apikey":...
                "wdsl":...

            },
            {
                "channel": "nomechannel2",
                "mu": "measurement_unit2",
                "column" : #2,
                "valid_range" : [start,end]
                "gwserial": "..."
                "apikey":...
                "wdsl":...
            },

            ...
            
            {
                "channel": "nomechannelN",
                "mu": "measurement_unitN",
                "column" : #N,
                "valid_range" : [start,end]
                "gwserial": "..."
                "apikey":...
                "wdsl":...
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


            print ("INFO_NEW:", info_new)

            try:
                gwserial=info_new.pop("gwserial")
            except Exception as e:
                gwserial=None

            try:
                apikey=f'#{info_new.pop("apikey")}'
            except Exception as e:
                apikey=None

            try:
                wsdl=info_new.pop("wsdl")
            except Exception as e:
                wsdl=None

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
                    operands={ "SER": serial, "COL":info["column"], "GW":gwserial, "KEY":apikey, "wsdl":wsdl},
                    operator=f"source.retrive(serials=SER,columns=COL,gateway=GW, key=KEY, wsdl=wsdl, times=times)",
                    valid_range=info['valid_range'],
                    view_range=info['view_range'],
                    thresholds=info['thresholds']
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

def retrive(serials=None, columns=None, gateway=None, key=None, wsdl=None, times=None):

    if isinstance(times,slice):
        start = times.start
        stop = times.stop
    else:
        start = times
        stop = None

    if start is None:
        start = 1

    if stop is None:
        stop = int(time())


    host='https://main.api.move-services.it'
    api='api/v3'
    gatway_id='641975b673fe125848cfce69'
    bearer_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0MTk3NTc0NTRjOThkNzAwMjViMmNiNyIsInJvbGUiOiJsb3JhIiwiaWF0IjoxNjc5MzkwMDY5fQ.9QqWG97fCdwVxtuQWo2WhTt0Div28LqN-4gv32AnJks'


    EUI='C0EE40000101F1D6'
    TYPE='accelerations'

    endpoint=f'{host}/{api}/sensors/{EUI}/measurements/{TYPE}?firstDate={start}&lastDate={stop}&page=0&sort=%2Bdate'



    if isinstance(start,(str,datetime)):
        start=int(datetime.fromisoformat(str(start)).timestamp())

    if isinstance(stop,(str,datetime)):
        stop=int(datetime.fromisoformat(str(stop)).timestamp())
              
    ahead=True
    out=DataFrame()

    while ahead:

        start="....."
        stop=datetime64(stop) + timedelta64(30,'D')

        response = requests.get(
                endpoint,
                headers = {
                    'accept': 'application/json',
                    'Authorization': 'Bearer '+bearer_key
                    })


        u= DataFrame(json.loads(response.content)['values'])[['date','acceleration']].set_index('date')['acceleration'].apply(Series)

        inner_ahead=True
        if u.__len__() < 50: ahead = False
              
        if u.__len__() > 0:
            ## VALUTARE I PARAMETRI SUCESSIVI
            u = u.set_index(['timeStamp'])['value']
            u.index.names=['timestamp']
            start = u.index.max() + 1
            out = concat([out,u])
            ##
    
    out = out.sort_index()
    out.columns = [f"{serials}_{columns}"]
    out.sort_index()
    out.index=to_datetime(out.index,unit='s')
              
    return out
              

