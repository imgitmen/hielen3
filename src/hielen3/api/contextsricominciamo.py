#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3.utils import ResponseFormatter
from hielen3 import db

#GET

# POST

@hug.get("/")
def ricominciamo(
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
    out = ResponseFormatter(status=falcon.HTTP_CREATED)

    try:
        try:
            rel2clean=list(db["context_context"][:]["ancestor"].values)

            if rel2clean.__len__():
                db["context_context"].pop(rel2clean)
        except KeyError as e:
            pass


        try:
            cntxt2clean=list(db["context"][:]["ID"].values)

            if cntxt2clean.__len__():
                db["context"].pop(cntxt2clean)
        except KeyError as e:
            pass

    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return

