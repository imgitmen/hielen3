#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
import os
import io
import PIL
import pandas as pd
import datamaps
import re


"""
.../PH/<element>/base ---- immagine di base
.../PH/<element>/timeline     ---- elenco timestamps
.../PH/<element>/map/?timestamp=....  immagine elaborata
.../PH/<element>/cld/?timestamp=....  immagine elaborata
.../PH/<element>/csv/?x=...&y=...&timefrom=...&timeto=...   serie dati
"""

def params(el):
    #el='glacier'
    return datamaps.parametrize(f'conf/{el}.json')

def dataset(el):
    #el='glacier'
    return datamaps.Render(**params(el))

def add_margin(img, x=0, y=0, color=(0,0,0,0)):
    width, height = img.size
    new_width = width + y*2
    new_height = height + x*2
    result = PIL.Image.new(img.mode, (new_width, new_height), color)
    result.paste(img, (y, x))
    return result

@hug.get('/{el}/base', examples='', output=hug.output_format.jpg_image)
def b1( el, request=None, response=None ):
    #el='glacier'
    return params(el)['background']

@hug.get('/{el}/timeline', examples='')
def b2( el, request=None, response=None ):
    #el='glacier'
    return dataset(el).timeline


@hug.get('/{el}/map', examples='', output=hug.output_format.png_image)
def b3( el, timestamp=None, output='RV', timeref=None, force:bool=False, background:bool=False, request=None, response=None ):

    #el='glacier'
    timestamp = datamaps.agoodtime(timestamp)
    timeref = datamaps.agoodtime(timeref)

    if timestamp is None:
        timestamp=dataset(el).timeline[-1]

    if timeref is None:
        timeref=dataset(el).reftime

    t1=re.sub('[^\d]','',str(timestamp))
    t2=re.sub('[^\d]','',str(timeref))

    savepath=os.path.join('incomes','cache',el,t2)

    savename=os.path.join(savepath,f'{t1}_{output}.png')

    if os.path.exists(savename) and not force:
        return savename

    os.makedirs(savepath, exist_ok=True)

    data_arr=dataset(el).generate_map(timestamp=timestamp,output=output,timeref=timeref, background=background)
    img=PIL.Image.fromarray(data_arr)
    img=add_margin(img,*params(el)['offset'])

    img.save(savename, format='PNG')
    
    return savename 


def get_df(el, x, y, timefrom=None, timeto=None, timeref=None, output="R"):

    #el='glacier'
    timefrom=datamaps.agoodtime(timefrom)
    timeto=datamaps.agoodtime(timeto)
    timeref=datamaps.agoodtime(timeref)

    d=dataset(el).extract_data(geom=(x,y),timefrom=timefrom,timeto=timeto,timeref=timeref,output=output)
    d.index.name='timestamp'
    d.columns=[f'{el}:displacement']
    return d


@hug.get('/{el}/data', examples='')
def b4( el, x, y, timefrom=None, timeto=None, timeref=None, output="R", request=None, response=None ):

    #el='glacier'
    d=get_df(el,x,y,timefrom,timeto,timeref,output)
    return hug.types.json(d.to_json(orient='table'))


@hug.get('/{el}/csv', examples='', output=hug.output_format.text)
def b5( el, x, y, timefrom=None, timeto=None, timeref=None, output="R",request=None, response=None ):

    #el='glacier'
    d=get_df(el,x,y,timefrom,timeto,timeref,output)
    return d.to_csv()


