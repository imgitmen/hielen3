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
            },
        {
            'type':'gestecno',
            'path':'gestecno'
            }
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        try:
            a=read_csv(path,skiprows=2,parse_dates=[0],header=None)
            if a.empty:
                a = read_csv(path,parse_dates=[0],header=None)
                a = a[a[0].apply(lambda x: match('^\d{4}-\d{2}',x)).notna()]

        except UnicodeDecodeError as e:
            a=read_csv(path,skiprows=3,parse_dates=[0], sep=";", header=None, encoding='latin1')

        a.columns = [ 'times', *a.columns[1:] ]
    
    except Exception as e:
        print("WARN : ", path)
        #raise e #DEBUG
        pass

    return a

