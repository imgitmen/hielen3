#!/usr/bin/env python
# coding=utf-8
import hug
import tempfile
import falcon
import os
import time
import json
from hielen2 import db
from hielen2.utils import hashfile
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from himada.api import ResponseFormatter
from urllib.parse import unquote

@hug.post('/{feature}/{form}',parse_body=False)
@hug.default_input_format( content_type='multipart/form-data')
def prots(feature=None,form=None, request=None, response=None, **kwargs ):

    out = ResponseFormatter(falcon.HTTP_ACCEPTED)

    try:
        t=db['features'][feature]['type']
        forms=db['features_proto'][t]['forms']
    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=f"feature '{feature}' does not exists or it is misconfigured."
        out.format(request=request,response=response)
        return

    try:
        form=forms[form]
    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=f"No '{form}' form defined for feature '{feature}'"
        out.format(request=request,response=response)
        return


    mandatory=form['mandatory'].keys()

    expected_fields={ **form['mandatory'], **form['optional'] }

    parser = StreamingFormDataParser(headers=request.headers)

    values={}

    for k,w in expected_fields.items():
        if w == 'file':
            t=time.perf_counter()
            filepath=os.path.join(tempfile.gettempdir(), f"{feature}{k}{t}.part")
            target=FileTarget(filepath)
            parser.register(k, target)
            values[k]=filepath
        else:
            target = ValueTarget()
            parser.register(k, target)
            values[k] = target

    while True:
        chunk = request.stream.read(8192)
        if not chunk:
            break
        parser.data_received(chunk)

    kwargs={}
    for k,w in values.items():
        
        if isinstance(w,str):
#FOR DUMMY RESPONSE
            v=os.path.exists(w) and "md5 "+hashfile(w) or None
#REAL
#            v=os.path.exists(w) and hashfile(w) or None
        else:
            v=unquote(w.value.decode('utf8')) or None

        kwargs[k]=v


    m = [ m for m in mandatory if kwargs[m] is None ]

    if m.__len__():
        out.status=falcon.HTTP_BAD_REQUEST
        out.message=f"Required parameters {m} not supplied"
        out.format(request=request,response=response)
        return

    return kwargs

