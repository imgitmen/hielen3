# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame, to_datetime 
from numpy import isin


folders=[
        {
            'type':'move',
            'path':'move'
            } 
        ]

func_loggers=loggers( folders )


'''
@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:

        a=read_csv(path, sep='\t', skiprows=3,header=None,index_col=[0]).iloc[:,4::3]
        a=a[~isin(a.index,"LOCAL TIME")]
        a.index=to_datetime(a.index,format='ISO8601')
        a=a.astype('float')

        a.index.name='times'
        a.columns=list(range(1,a.columns.__len__()+1))
        a=a.reset_index()

        #a.columns = [ 'times', *a.columns[1:] ]
    
    except Exception as e:
        #print("WARN : ", path)
        #raise e #DEBUG
        a=DataFrame([],dtype='float64')
        pass

    return a
'''
