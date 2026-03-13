# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame, Series, concat, to_datetime

folders=[
        {
            'type':'loadsensing_gps',
            'path':'loadsensing/gps'
            },
        ]

func_loggers=loggers( folders )

@retriver(func_loggers)
def retrive(path):

    a=DataFrame([],dtype='float64')

    try:
        if "converted" in str(path):
            a=read_csv(path,skiprows=1,header=None)
            a.columns = [ 'times', *a.columns[1:] ]
            a["times"]=a["times"].astype(str).str.strip()

    except Exception as e:
        print("WARN : ", path)
        a=DataFrame([],dtype='float64')
        #raise e #DEBUG
        pass

    return a


