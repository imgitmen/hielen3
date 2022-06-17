# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame 

folders=[
        {
            'type':'ominalog',
            'path':'omnialog'
            } 
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        a=read_csv(path,skiprows=1,parse_dates=[0],header=None)
        a.columns = [ 'times', *a.columns[1:] ]
    
    except Exception as e:
        #raise e
        pass

    return a

