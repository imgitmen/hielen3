# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame
from pandas.errors import EmptyDataError 

folders=[
        {
            'type':'boviar',
            'path':'boviar'
            } 
        ]

func_loggers=loggers( folders )


@retriver(func_loggers)
def retrive(path):
    a=DataFrame([],dtype='float64')

    try:
        a=read_csv(path,sep=';',skiprows=14,header=None,parse_dates=[0],dayfirst=True,index_col=[0])
        a.columns=map(lambda x: x.replace(" ","_").replace("+5V","p5V"), read_csv(path,sep=';',skiprows=11,nrows=1,header=None,index_col=0).T.squeeze().values)
        a.index.name='times'
        a=a.reset_index()

    except EmptyDataError as e:
        pass
    
    except Exception as e:
        raise e
        pass

    return a

