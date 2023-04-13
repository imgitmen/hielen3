#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
from hielen3 import db
from hielen3.utils import JsonValidable, hasher, ResponseFormatter, uuid, dataframe2jsonizabledict
from hielen3.feature import HFeature
from hielen3.geje import GeoJSONSchema
from pandas import Series
from marshmallow import Schema, fields
import traceback


@hug.get("/")
def features_info(uids=None, request=None, response=None):

    """
    """

    out = ResponseFormatter()

    try:
            
        feafra=db['awskine'][uids]
        feafra=dataframe2jsonizabledict(feafra,orient='index',squeeze=False)

        out.data = { "resources":feafra }
        feafra=None

    except KeyError as e:
        out.data = { "resources":[] }
        #out.status = falcon.HTTP_NOT_FOUND
        out.message = e.args

    response = out.format(response=response, request=request)

    return


@hug.get("/{uid}")
def feature_info(uid, request=None, response=None):
    """
    """
    return features_info(uid, request, response)
