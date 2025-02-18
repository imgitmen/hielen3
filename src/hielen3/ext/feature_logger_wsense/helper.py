# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame 
from re import sub

folders=[
        {
            'type':'wsense',
            'path':'wsense/data'
            },
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        a=read_csv(path,sep=',',parse_dates=[0],dayfirst=False)
        a.columns=[ 'times',*list(  range(1,a.columns.__len__())) ]
    
    except Exception as e:
        print("WARN : ",e, path)
        #raise e #DEBUG
        pass

    return a

