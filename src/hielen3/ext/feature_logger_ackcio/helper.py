# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame 
from re import sub

folders=[
        {
            'type':'ackcio',
            'path':'ackcio/data'
            },
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    if 'NodeData' in str(path):
        return a

    try:
        a=read_csv(path,parse_dates=[0])
        a.columns=a.columns.to_series().apply(lambda x: sub(' (.+)','',x))
        a.columns=[ 'times',*list(a.columns[1:]) ]
    
    except Exception as e:
        #print("WARN : ",e, path)
        #raise e #DEBUG
        pass

    return a

