#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3.tools import hls_facility as hls
from hielen3.utils import ResponseFormatter

@hug.get("/{queue}")
def retrive(queue,request=None,response=None):

    out = ResponseFormatter()

    out.data,outcode=hls.get_stream(queue)

    if outcode == 404:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"queue not found: {queue}"

    out.format(request=request,response=response)

    return



    


