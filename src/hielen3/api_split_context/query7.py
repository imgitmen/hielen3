#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
import tempfile
from pathlib import Path
from marshmallow import Schema
from marshmallow import fields
from numpy import nan
from numpy import unique
from numpy import datetime64
from numpy import timedelta64
from pandas import DataFrame
from pandas import to_datetime
from pandas import to_numeric
from pandas import concat
from hielen3 import db
from hielen3.series import HSeries
from hielen3.utils import JsonValidable
from hielen3.utils import Selection
from hielen3.utils import ResponseFormatter
from hielen3.utils import uuid
from hielen3.utils import dataframe2jsonizabledict
from hielen3.utils import boolenize
from hielen3.geje import GeoJSONSchema
from hielen3.tools.log_regression import hielen_log_reg 


CSV = "text/plain; charset=utf-8"
JSON = "application/json; charset=utf-8"
XLSX = "file/dynamic"

class DataMapSchema(Schema):

    """"""
    times = Selection(missing=slice(None),default=slice(None), required=False, allow_none=True)
    timeref = fields.Str(default=None, required=False, allow_none=True)
    series = fields.List(fields.Str, default=[])
    refresh = fields.Bool(default=False, required=False, allow_none=True) #NON SERVE A UNA CIPPA DE CAZZO 
    geometry = fields.List(fields.Nested(GeoJSONSchema, required=False, allow_none=True),default=[])


####### Gestore di API DATATABLE se cache='old' o null
def capability_data_cache_old(datamap, capability):

    out=DataFrame()

    for query in datamap:

        try:
            times=query["times"]
        except KeyError as e:
            times=slice(None,None)

        req_series=query.pop('series')

        try:
            ss=db['series'][req_series]
            ss=list(ss[ss['capability']==capability]['uuid'].values)
        except KeyError as e:
            ss = None

        if ss is not None:
            
            info=db["series"][ss][["datatable","first"]]


            tabella=info[["datatable"]].dropna()
            letzero=info[["first"]].dropna()

            if not tabella.empty:
                raggruppamento=tabella.reset_index().set_index("datatable")
                dati=raggruppamento.groupby("datatable").apply(lambda x: list(x["uuid"].values))

                for k,w in dati.groupby("datatable"):

                    columns=w.squeeze()
                    try:
                        estrazione=db[k][columns,times]
                    except KeyError as e:
                        estrazione=DataFrame([],columns=columns)

                    out=concat([out,estrazione])


            if not letzero.empty:

                raggruppamento=letzero.reset_index().set_index("first")
                primi=raggruppamento.groupby("first").apply(lambda x: list(x["uuid"].values))


                for k,w in primi.groupby("first"):

                    k= str(datetime64(k) - timedelta64(1,"s"))
        
                    columns=w.squeeze()
                    try:
                        out.loc[:k,columns] = nan
                    except KeyError as e:
                        pass



                #out=out[~(out.apply(lambda x: x.notna(),axis=1).any())]

    out=out.apply(to_numeric,errors='coerce').round(4)
    out=out[~out.isna().all(axis=1)]

    return out


####### API DATATABLE #######
@hug.post("/{capability}", examples="")
@hug.get("/{capability}", examples="")
def tabular_data(
        capability,
        datamap: JsonValidable(DataMapSchema(many=True)),
        stats=None,
        content_type=None,
        cache='old',
        regression=None,
        request=None,
        response=None,
        **kwargs
):

    series = {}
    out = ResponseFormatter()

    if content_type is None:
        content_type = CSV

    stats=boolenize(stats,False)

    merged_series_uuids=[]

    try:
        for rq in datamap:
            for rs in rq["series"]:
                merged_series_uuids.append(rs)
    except Exception as e:
        pass

    merged_series_uuids=list(set(merged_series_uuids))

    if cache != "old" or capability != "data": 
    
        kwargs["cache"] = cache

        for query in datamap:

            #ss = query.pop('series')

            try:
                ss=db['series'][query.pop('series')]
                ss=list(ss[ss['capability']==capability]['uuid'].values)
            except KeyError as e:
                out.status=falcon.HTTP_NOT_FOUND
                out.message = str(e) + " not found"
                response = out.format(response=response, request=request)
                return

            for p in ss:
                if p not in series.keys():
                    series[p] = []

                series[p].append( HSeries(p).thvalues(**query,**kwargs) )
               
        df = DataFrame()

        for param, sers in series.items():

            ser = None
            for r in sers:
                s = r.result()
                if ser is None:
                    ser = s
                else:
                    ser = concat([ser,s]).sort_index()
                    ser = ser[~ser.index.duplicated()]


            df = df.join(ser, how="outer")
   
        if capability == 'datadiagram':
            try:
                col_ordered=db["series_groups"][{"element":df.columns.to_list()}][["element","ordinal"]].reset_index("groupseries").sort_values(["groupseries","ordinal"])["element"].to_list()
                df=df[col_ordered]
            except Exception as e:
                pass
    
    else:
        try:
            df = capability_data_cache_old(datamap, capability) 
        except KeyError as e:
            df = DataFrame()

            """
            out.status=falcon.HTTP_NOT_FOUND
            out.message = str(e) + " not found"
            response = out.format(response=response, request=request)
            return
            """

    try:
        df=df.to_frame()
    except Exception as e:
        pass

    df.index.name = "timestamp"

    if stats:

        span = 1000 #TODO prevederlo come parametro 

        stats=df.index.to_series().describe()[["min","max","count"]]
        count=stats[["count"]].copy()
        stats=stats[["min","max"]].copy().astype("datetime64[ns]")
        count["step"]=(count.astype(float) / span).round(0).astype(int).squeeze()
        df=concat([stats,count]).to_frame().T
        df.index.name='range'

        if request is None:
            return df

        out.data = dataframe2jsonizabledict(df,squeeze=False) 
        response = out.format(response=response, request=request)
        response.content_type = JSON
        return
    
    if regression == "log":
        if capability == "datadiagram" and merged_series_uuids.__len__() == 1:
            df = hielen_log_reg(df,merged_series_uuids[0])


    if request is None:
        return df

    if content_type in CSV:

        #txtout = hug.types.text(df.to_csv(sep=';',date_format="%Y-%m-%d %H:%M:%S"))
        txtout = df.to_csv(sep=';',date_format="%Y-%m-%d %H:%M:%S")
        response.content_type=CSV
        response.body=txtout
        return

    if content_type in JSON:
        df.index=df.index.astype('str')
        df = df.replace({nan:None})
        out.data={}

        if df.empty:
            for s in df.columns:
                out.data[s] = []

        else:

            out.data=json.loads(df.to_json())

            """
            grp=df.apply(lambda x: x.reset_index().values.tolist()).T.groupby("series")
            for s,g in grp:
                out.data[s]=g.loc[s].values.tolist()
            """


        response = out.format(response=response, request=request)
        response.content_type=JSON
        return
    
    if content_type in XLSX:

        try:
            h=db['features_parameters_headers_v2'][list(df.columns)]
            h=h[~h["series"].duplicated()][["series","flabel","param"]]
            h.index=h.series
            df=df.T.join(h).set_index(['flabel','param','series']).sort_index().T
        except Exception as e:
            pass

        df.index.name='timestamp'
        filepath = Path(tempfile.gettempdir(), f"{uuid()}.xlsx")
        df.to_excel(filepath)
        response.content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.stream = open(filepath, 'rb')
        response.set_header('Content-Disposition', 'attachment; filename="readings.xlsx"')

        return response.stream


@hug.get("/{capability}/{feature}/")
def tabular_data_el(
        capability,
        feature,
        par=None,
        times=None,
        timeref=None,
        refresh=None,
        geometry=None,
        content_type=None,
        request=None,
        response=None,
        **kwargs
):


    if isinstance(geometry,list):
        geometry = ",".join(geometry)

    if geometry is None:
        geometry = "[]"

    try:
        feature=feature.split(",")
    except Exception:
        pass
    try:
        par=par.split(",")
    except Exception:
        pass

    try:
        series=list(db['features_parameters'][feature,par]['series'].values)
    except KeyError as e:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message = str(feature) + " not found"
        response = out.format(response=response, request=request)
        return

    datamap = dict(series=series, times=times, timeref=timeref, geometry="#PLACEHOLDER#", refresh=refresh)

    #print (datamap)


    datamap=json.dumps(datamap).replace('"#PLACEHOLDER#"',geometry)

    datamap = DataMapSchema().loads(datamap)

    return tabular_data(capability=capability, datamap=[datamap], content_type=content_type, request=request, response=response,**kwargs)


@hug.get("/{capability}/{feature}/{par}")
def tabular_data_par(
        capability,
        feature,
        par,
        times=None,
        timeref=None,
        refresh=None,
        geometry=None,
        content_type=None,
        request=None,
        response=None,
        **kwargs
):

    return tabular_data_el(
        capability=capability,
        feature=feature,
        par=par,
        times=times,
        timeref=timeref,
        refresh=refresh,
        geometry=geometry,
        content_type=content_type,
        request=request,
        response=response,
        **kwargs
    )

