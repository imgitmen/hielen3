# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame 

folders=[
        {
            'type':'leica',
            'path':'leica/EXPORT'
            },
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        a=read_csv(path,parse_dates=[0])
        #a.columns=[ 'times',*list(range(1,a.columns.__len__()))]
        a.columns = [ 'times', *a.columns[1:] ]
    
    except Exception as e:
        print("WARN : ", path)
        #raise e #DEBUG
        pass

    return a

