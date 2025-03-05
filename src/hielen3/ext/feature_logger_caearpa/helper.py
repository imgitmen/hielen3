# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame, to_numeric, Series 
from re import sub

folders=[
        {
            'type':'caearpa',
            'path':'caearpa'
            },
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        a=read_csv(path,sep=';',header=None)
        a=a[a[0].apply(lambda x: "DTL" in x)][0].apply(str.split, sep = '\t').apply(Series)[[0,1,2]]
        a[0] = a[0].apply(lambda x: f"SN_{x}")
        a[1]=a[1].astype('datetime64[ns]')
        a=a.set_index([1,0]).unstack()
        a.columns.names=["al","serial"]
        a.columns=a.columns.droplevel("al")
        a.columns.names=[None]
        a = a.reset_index()
        a.columns=[ 'times',*a.columns[1:]]

    except Exception as e:
        print("WARN : ",e, path)
        #raise e #DEBUG
        pass

    return a

