#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
from marshmallow import Schema, fields
from numpy import nan, unique
from pandas import DataFrame, to_datetime
from hielen3 import db
from hielen3.series import HSeries
from hielen3.utils import hug_output_format_conten_type, JsonValidable, Selection, ResponseFormatter
from hielen3.geje import GeoJSONSchema

data_out_handler = hug_output_format_conten_type(
    [hug.output_format.json, hug.output_format.text]
)
CSV = "text/plain; charset=utf-8"
JSON = "application/json; charset=utf-8"


class DataMapSchema(Schema):

    """"""
    times = Selection(missing=slice(None),default=slice(None), required=False, allow_none=True)
    timeref = fields.Str(default=None, required=False, allow_none=True)
    series = fields.List(fields.Str, default=[])
    refresh = fields.Bool(default=False, required=False, allow_none=True)
    geometry = fields.List(fields.Nested(GeoJSONSchema, required=False, allow_none=True),default=[])


####### API DATATABLE #######
@hug.get("/{capability}", examples="", output=data_out_handler)
def tabular_data(
        capability,
        datamap: JsonValidable(DataMapSchema(many=True)),
        content_type=None,
        request=None,
        response=None,
        **kwargs
):

    series = {}

    for query in datamap:

        ss = query.pop('series')

        for p in ss:
            
            if p not in series.keys():
                series[p] = []

            try:
                series[p].append( HSeries(p,orient=capability).thvalues(**query,**kwargs) )
            except KeyError as e:
                out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
                out.message = str(e) + " not found"
                response = out.format(response=response, request=request)
                return

    out = DataFrame()

    for param, sers in series.items():

        ser = None
        for r in sers:
            s = r.result()
            if ser is None:
                ser = s
            else:
                ser = ser.append(s).sort_index()
                idx = unique(ser.index.values, return_index=True)[1]
                ser = ser.iloc[idx]

        try:
            ser.columns = [ "_".join([param,a]) for a in ser.columns]
        except Exception as e:
            ser.name=param

        out = out.join(ser, how="outer")

    out.index.name = "timestamp"

    requested = data_out_handler.requested(request).content_type
    
    if requested == CSV:
        return hug.types.text(out.to_csv(sep=';',date_format="%Y-%m-%d %H:%M:%S"))
    if requested == JSON:
        return hug.types.json(out.to_json(orient="table"))


@hug.get("/{capability}/{feature}/", output=data_out_handler)
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
    except KeyError:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message = str(feature) + " not found"
        response = out.format(response=response, request=request)
        return

    datamap = dict(series=series, times=times, timeref=timeref, geometry="#PLACEHOLDER#", refresh=refresh)
    datamap=json.dumps(datamap).replace('"#PLACEHOLDER#"',geometry)

    datamap = DataMapSchema().loads(datamap)

    return tabular_data(capability=capability, datamap=[datamap], content_type=content_type, request=request, response=response,**kwargs)


@hug.get("/{capability}/{feature}/{par}", output=data_out_handler)
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
