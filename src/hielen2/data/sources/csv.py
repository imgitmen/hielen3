# coding: utf-8
from pandas import DataFrame, Series, to_datetime, read_csv
import json
import requests

def get_ch(path='./incomes',restype=None,resource=None,filename='last_load.csv',column=None,timefrom=None,timeto=None):
    return GWO(path,restype,filename).getDataSeries(resource=resource,column=column,timefrom=timefrom,timeto=timeto)

class GWO():

    def __init__(self,path='./incomes',restype=None,filename='last_load.csv'):
        self.path=path
        self.restype=restype
        self.filename=filename

    def getDataSeries(self,resource=None,column=None,timefrom=None,timeto=None):

        out=read_csv(f"{self.path}/{self.restype}/{resource}/{self.filename}",header=None,index_col=[0])[column]
        #out.index=to_datetime(out.index)
        out=out.loc[timefrom:timeto]
        return out

