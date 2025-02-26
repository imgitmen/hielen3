# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame, to_numeric, Series 
from re import sub

folders=[
        {
            'type':'gei',
            'path':'gei/data'
            },
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        
        a=read_csv(
                path,sep="|", header=None, parse_dates=[0], dayfirst=True, index_col=0).\
                        stack().\
                        apply(str.split, sep=";").\
                        apply(Series)[[1,2]].\
                        unstack().\
                        stack(0).\
                        unstack().\
                        apply(to_numeric, errors='coerce').\
                        sort_index().\
                        reset_index()

        a.columns=[ 'times',*list(  range(1,a.columns.__len__())) ]
    
    except Exception as e:
        print("WARN : ",e, path)
        #raise e #DEBUG
        pass

    return a

