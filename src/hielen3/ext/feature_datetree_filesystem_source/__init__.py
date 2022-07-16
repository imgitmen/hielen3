# coding=utf-8

__name__ = "Feature_datetree_filesystem_source"
__version__ = "0.0.1"
__author__ = "Alessandro Modesti"
__email__ = "it@img-srl.com"
__description__ = "HielenSource extensione"
__license__ = "MIT"
__uri__ = ""


from hielen3 import conf
from pathlib import Path 
import traceback

from glob import glob
from pathlib import Path
from pandas import DataFrame, read_csv, concat
from datetime import datetime


def loggers( folders ):

    def inner():
        return logger_serials(folders)
    return inner


def logger_serials( folders={} ):

        # DA INSERIE IN CONFING

        folders=DataFrame(folders)
        folders=folders.set_index('type')

        folders=folders['path'].apply( lambda x: str(Path(conf['incomepath'] , x , "*")) ).apply(glob).explode().apply(Path)

        folders=folders[
                folders.apply(Path.is_dir)
                ].to_frame().apply(
                        lambda x: { "path":x['path'].parent, "name":x['path'].name},axis=1,result_type='expand'
                        )

        return folders.sort_values(by='name')



def retriver( func_loggers  ):

    def wrap( func_extract ):

        def inner(*args,**kwargs):
            return retrive(*args,func_extract=func_extract,func_loggers=func_loggers,**kwargs)

        return inner

    return wrap


def retrive(serials=None,times=None, columns=None, func_extract=None, func_loggers=None, **kwargs ):

    def __default_extract__(*args,**kwargs):
        return DataFrame()

    def __default_folders__(*args,**kwargs):
        return []

    if func_extract is None:
        func_extract = __default_extract__

    if func_loggers is None:
        func_folders = __default_folders__


    if serials is None:
        serials = slice(None,None)

    if isinstance(serials,str):
          serials=[serials]

    if isinstance(times,datetime):
        times=str(times)

    if times is None or isinstance(times,str):
        times=slice(times,None,None)
    
    start=times.start
    stop=times.stop

    if start is not None:
        datestart=str(datetime.fromisoformat(start).date())
    else:
        datestart=None

    times=slice(start,stop)

    dates=slice(datestart,stop)

    folders=func_loggers().set_index('name')

    df=DataFrame(dtype='object')

    if isinstance(serials, (list,set,tuple)):
        serials=list(folders.index[
                folders.index.isin(serials)
                ].drop_duplicates())

        if not serials.__len__():
            return df
 

    paths=folders.loc[serials].reset_index().apply(lambda x: str( x['path'] / x['name'] / "*" / "*" / "*" ), axis=1).apply(glob).explode().apply(Path)

    sertime=DataFrame(
                paths.apply( lambda x: 
                    (
                        x.parts[-4], 
                        str(datetime(*map(int,x.parts[-3:])))
                        )
                    ).explode().values.reshape(paths.__len__(),2),
                columns=['serial','times']
            )


    paths.index=sertime.index

    sertime['path']=paths.apply(lambda x: str(x / "*"))
    sertime=sertime.set_index(['serial','times']).sort_index()


    try:
        sertime=sertime.to_frame()
    except Exception as e:
        pass

    try:
        sertime=sertime.loc[(serials,dates), :]
    except KeyError as e:
        return df


    for serial,paths in sertime.groupby('serial'):
        u=concat(paths['path'].apply(glob).explode().apply(func_extract).values)
        u['serial']=serial
        u=u.set_index(['serial','times'])
        df=concat([df,u])

    if columns is None:
        columns = list(df.columns)

    if not isinstance(columns,(list,tuple,set)):
        columns=[columns]

    columns=list(columns)

    columns=[ c for c in columns if c in df.columns ]

    df=df[columns].sort_index().loc[(serials, times), :]

    try:
        if serials.__len__() == 1:
            df = df.droplevel('serial',axis=0)
    except Exception as e:
        pass

    return df



__all__ = ["retriver", "loggers" ]

