#!/usr/bin/env python
# coding=utf-8
import hug
import tempfile
import falcon
import os
import time
import json
from hielen2 import db, conf
import hielen2.source as sourceman
from himada.api import ResponseFormatter

import traceback

@hug.get('/map/')
def map(features, timestamp=None, output=None, request=None, response=None):

    """

"""
    out = ResponseFormatter()

    # Trying to manage income feature request and its prototype configuration
    try:
        feat = db["features"][features]
        featobj = sourceman.sourceFactory(feat,conf['filecache'])
        featobj.map(timestamp)
    except Exception as e:
        traceback.print_exc()
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{features}' does not exists or it is misconfigured: {e}"
        out.format(request=request, response=response)
        return

    out.format(request=request, response=response)
    return


@hug.get('/map/{feature}')
def map_feat(feature,timestamp=None, output=None, request=None, response=None):
    return map(feature,timestamp,output,request,response)
    
"""
@hug.get('/map/{feature}/{param}')
def map_feat_param():
    pass

@hug.get('/timeline')
def timeline():
    pass

@hug.get('/timeline/{feature}')
def timeline_feat():
    pass

@hug.get('/timeline/{feature}/{param}')
def timeline_feat():
    pass
"""
