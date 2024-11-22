#!/usr/bin/env python
# coding=utf-8
import hug
from hielen3.tools import hls_facility as hls
from hielen3.utils import ResponseFormatter

@hug.post("/")
def submit(resource=None,request=None, response=None):

    out = ResponseFormatter()

    out.data,outcode=hls.start_stream(resource)

    print (out.data,outcode)

    if outcode == 400:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"resource not found: {resource}"

    out.format(request=request,response=response)

    return

@hug.post("/{resource}")
def submitr(resource=None,request=None,response=None):
    return submit(resource=resource,request=request,response=response)

