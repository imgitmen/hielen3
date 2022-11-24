#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3 import db
from hielen3.utils import ResponseFormatter, dataframe2jsonizabledict
import traceback

@hug.get("/")
def fands_status(uids=None, cntxt=None, request=None, response=None):

    out = ResponseFormatter()

    if cntxt is not None and not isinstance(cntxt,list):
        if cntxt == "":
            cntxt = None
        else:
            cntxt = [cntxt]

    try:
            
        feafra=db['status'][uids,cntxt]

        feafra=dataframe2jsonizabledict(feafra.droplevel("context"),orient='records',squeeze=False)

        out.data = feafra
        feafra=None

    except KeyError as e:
        out.data = []
        out.message = e.args

    response = out.format(response=response, request=request)

    return

@hug.get("/{uid}")
def ffandss_status(uid, cntxt=None, request=None, response=None):
    return fands_status(uid, cntxt, request, response)

