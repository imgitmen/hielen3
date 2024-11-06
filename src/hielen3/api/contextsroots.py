#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3.utils import ResponseFormatter
from hielen3.utils import clean_input
from hielen3.contextmanager import roots_info

#GET

@hug.get("/")
def get_roots_param(
    cntxt=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    cntxt=clean_input(cntxt)

    try:
        out.data=roots_info(cntxt).to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return

@hug.get("/{cntxt}")
def get_roots_endpoint(
    cntxt=None,
    request=None,
    response=None,
    **kwargs
):

    return get_roots_param(cntxt,request,response,**kwargs)


