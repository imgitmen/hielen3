# coding: utf-8
from pandas import DataFrame, Series, to_datetime
import json
import requests

def get_ch(sito=None,id_stazione=None,id_unita=None,id_sensore=None,aggr='avg',timefrom=None,timeto=None):
    return GWO().getDataSeries(sito=sito,stazione=id_stazione,unita=id_unita,sensore=id_sensore,aggr='avg',timefrom=timefrom,timeto=timeto)

class GWO():

    def __init__(self,uri='https://www.smori.it/tisma/api/v1/sensor_data.php'):
        self.uri=uri

    def getDataSeries(self,sito=None,stazione=None,unita=None,sensore=None,aggr='avg',timefrom=None,timeto=None):

        params=dict(
                sito=sito,
                stazione=stazione,
                unita=unita,
                sensore=sensore,
                )

        if aggr is not None:
            params['aggr']=aggr

        if timefrom is not None:
            params['dal']=timefrom

        if timefrom is not None:
            params['al']=timeto

        r = requests.get(url=self.uri, params=params)

        out=DataFrame(json.loads(r.text)['data'])

        #print (r.url)

        if out.empty:
            return out

        out = out.set_index(['timestamp'])['valore']

        out=out.astype(float, copy=False, errors='ignore')

        out.name = f"{stazione}_{unita}_{sensore}"
        out.index=to_datetime(out.index)

        return out

