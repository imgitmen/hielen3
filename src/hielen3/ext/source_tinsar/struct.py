# coding: utf-8
import pandas as pd
import hielen3.ext.source_tinsar.cloudpainter as cloudpainter
from pathlib import Path


def make_laz_clouds(csvfile,targetpath=None,sep=" ",fields=None,scale=[0.000001,0.000001,0.000001], field_cmaps=None):

    if fileds is None:
        fields = ['base']

    if not isinstance(fields,str):
        fields = [fields]

    fields = list(map(str.lower),fields)

    try:
        targetpath = Path(tergetpath)
    except Exception as e:
        targetpath = Path(".")

    #We expect header
    cloud=pd.read_csv(csvfile,sep=sep)

    cloud.columns=list(map(str.lower),cloud.columns)

    lazdone={}

    for c in fields:

        try:
            cmap=field_cmaps[c]
        except KeyError as e:
            cmap={}

        if c == 'base':
            theframe=cloud[['x','y','z','r','g','b']]
        else:
            theframe=cloudpainter.paint(cloud[['x','y','z',c]],**cmap)[['x','y','z','r','g','b']]

        colormult=65536
        colormult=255
        colormult=1

        #colors='jet'

        lazpath=str(targetpath / f'{c}.laz')

        cloudpainter.makelaz(theframe, lazpath, scale=scale, colormult=1)

        lazdone[c]=lazpath


    return lazdone
    """

r=parse_colormap(make_colormap([[-100, "#ee55ee"], [ -66.6 ,"#0000ff"] , [-33.3, "#00ffff" ],[0,"#00FF00"] ,[ 33.3, "#ffff00"], [ 66.6,"#ffa500" ], [ 100, "#FF0000" ]]))

r={
        'cmap':ListedColormap(["#ee55ee", "#0000ff","#00ffff","#00FF00","#ffff00","#ffa500","#FF0000"],'Custom_map'),
        'norm':Normalize(vmin=-50,vmax=50)
        }

result=cloudpainter_new.paint(spostamento,**r)
cloudpainter_new.makelaz(result[['x','y','z','r','g','b']],'spostamento.laz',colormult=255, scale=[0.000001,0.000001,0.000001])

"""

