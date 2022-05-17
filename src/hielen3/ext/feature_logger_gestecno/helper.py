# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame 

folders=[
        {
            'type':'gestecno',
            'path':'gestecno_rfi/data'
            }, 
        {
            'type':'gestecno',
            'path':'gestecno_saa/diag'
            }
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        a=read_csv(path,skiprows=2,parse_dates=True,header=None)
        if a.empty:
            a = read_csv(path,parse_dates=True,header=None)
            a = a[a[0].apply(lambda x: match('^\d{4}-\d{2}',x)).notna()]

        a.columns = [ 'times', *a.columns[1:] ]
    
    except Exception as e:
        #raise e
        pass

    return a

