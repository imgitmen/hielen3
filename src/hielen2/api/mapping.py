#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
from marshmallow import Schema, fields
from numpy import nan, unique
from pandas import DataFrame, to_datetime
from hielen2 import db
from hielen2.maps.data_access_layer import Series
from hielen2.utils import hug_output_format_conten_type, JsonValidable, Selection
from himada.api import ResponseFormatter
import asyncio


data_out_handler = hug_output_format_conten_type(
    [hug.output_format.text, hug.output_format.json]
)
CSV = "text/plain; charset=utf-8"
JSON = "application/json; charset=utf-8"


class DataMapSchema(Schema):

    """"""
    times = Selection(missing=slice(None),default=slice(None), required=False, allow_none=True)
    timeref = fields.Str(default=None, reuired=False, allow_none=True)
    series = fields.List(fields.Str, default=[])
    refresh = fields.Bool(default=False, required=False, allow_none=True)


####### API DATATABLE #######
@hug.get("/", examples="", output=data_out_handler)
def tabular_data(
    datamap: JsonValidable(DataMapSchema(many=True)),
    content_type=None,
    request=None,
    response=None,
):

    series = {}

    for s in datamap:

        for p in s["series"]:

            if p not in series.keys():
                series[p] = []
            try:
                series[p].append(Series(p).thdata(s['times'],s['timeref'],s['refresh']))
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


        #ser.columns = [param]
        ser.name = param

        out = out.join(ser, how="outer")

    out.index.name = "timestamp"

    requested = data_out_handler.requested(request).content_type

    if requested == CSV:
        return hug.types.text(out.to_csv(sep=';'))
    if requested == JSON:
        return hug.types.json(out.to_json(orient="table"))


@hug.get("/{feature}/", output=data_out_handler)
def tabular_data_el(
    feature,
    par=None,
    times=None,
    timeref=None,
    refresh=None,
    content_type=None,
    request=None,
    response=None,
):

    try:
        ft = db["features"][feature]
    except KeyError:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message = str(feature) + " not found"
        response = out.format(response=response, request=request)
        return
    try:

        if par is None:
            series = list(ft["parameters"].values())
        else:
            series = [ft["parameters"][par]]

    except KeyError as e:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message = str(e) + " not found"
        response = out.format(response=response, request=request)
        return


    datamap = dict(series=series, times=times, timeref=timeref, refresh=refresh)
    datamap = DataMapSchema().loads(json.dumps(datamap))

    return tabular_data(datamap=[datamap], request=request, response=response)


@hug.get("/{feature}/{par}", output=data_out_handler)
def tabular_data_par(
    feature=None,
    par=None,
    times=None,
    timeref=None,
    refresh=None,
    content_type=None,
    request=None,
    response=None,
):
    return tabular_data_el(
        feature=feature,
        par=par,
        times=times,
        timeref=timeref,
        refresh=refresh,
        request=request,
        response=response,
    )
