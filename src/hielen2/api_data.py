#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
from .utils import hug_output_format_conten_type
from numpy import nan, unique
from pandas import DataFrame, to_datetime
from hielen2 import db
from hielen2.data.data_access_layer import Series
from himada.api import ResponseFormatter
import asyncio


data_out_handler=hug_output_format_conten_type([hug.output_format.text,hug.output_format.json])
CSV="text/plain; charset=utf-8"
JSON="application/json; charset=utf-8"


####### API DATATABLE #######
@hug.get('/', examples='', output=data_out_handler)
def tabular_data( datamap, request=None, response=None ):

    if isinstance (datamap,list):
        datamap=','.join(datamap)
    
    try:
        loaded=json.loads(datamap)
    except json.JSONDecodeError as e:
        out = ResponseFormatter(status=falcon.HTTP_BAD_REQUEST)
        out.message=str(e)
        response = out.format(response=response,request=request)
        return

    series={}

    for s in loaded:
        try:
            timefrom=s['timefrom']
        except KeyError:
            timefrom=None
        try:
            timeto=s['timeto']
        except KeyError:
            timeto=None

        for p in s['series']:

            if p not in series.keys():
                series[p]=[]

            try:
                series[p].append( Series(p).thdata(timefrom=timefrom,timeto=timeto) )
            except KeyError as e:
                out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
                out.message=str(e) + " not found"
                response = out.format(response=response,request=request)
                return

    out=DataFrame()

    for param,sers in series.items():

        ser=None
        for r in sers:
            s=r.result()
            if ser is None:
                ser = s
            else:
                ser = ser.append(s).sort_index()
                idx= unique( ser.index.values, return_index = True )[1]
                ser=ser.iloc[idx]

        ser.columns=[param]

        out = out.join(ser,how='outer')

    out.index.name='timestamp'
    
    requested=data_out_handler.requested(request).content_type

    if (requested==CSV):
        return hug.types.text(out.to_csv())
    if (requested==JSON):
        return hug.types.json(out.to_json(orient='table'))


@hug.get('/{el}/', output=data_out_handler)
def tabular_data_el( el, par=None, timefrom=None, timeto=None, request=None, response=None ):
  
    try:
        element=db['elements'][el]
    except KeyError:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)                       
        out.message=str(el) + " not found"                                           
        response = out.format(response=response,request=request)                    
        return 

    
    
    try:
    
        if par is None:
            parameters=[ f"{element['code']}:{e}" for e in element['parameters'].keys() ]
        else:
            parameters=[ f"{element['code']}:{par}" ]

    except KeyError as e:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message=str(e) + " not found"
        response = out.format(response=response,request=request)
        return

    datamap=dict(parameters=parameters)

    if timefrom is not None:
        datamap['timefrom']=timefrom

    if timeto is not None:
        datamap['timeto']=timeto

    return tabular_data(datamap=json.dumps([datamap]),request=request,response=response)
    



@hug.get('/{el}/{par}', output=data_out_handler)
def tabular_data_par( el=None, par=None, timefrom=None, timeto=None, request=None, response=None ):

    return tabular_data_el( el=el,par=par,timefrom=timefrom,timeto=timeto,request=request, response=response )




