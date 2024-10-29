#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3 import db
from hielen3.utils import ResponseFormatter

#GET

@hug.get("/")
def get_context_param(
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

    try:
        out.data=db["context"][cntxt].to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR

    response = out.format(response=response, request=request)

    return

@hug.get("/{cntxt}")
def get_context_endpoint(
    cntxt=None,
    request=None,
    response=None,
    **kwargs
):

    return get_context_param(cntxt,request,response,**kwargs)



# POST

@hug.post("/")
def create_context(
    cntxt,
    label=None,
    description=None,
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
        db["context"][cntxt]={"label":label,"description":description}
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR

    response = out.format(response=response, request=request)

    return

@hug.delete("/")
def delete_context_param(
    cntxt,
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

    try:
        out.data=db["context"].pop(cntxt).to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR

    response = out.format(response=response, request=request)

    return

@hug.delete("/{cntxt}")
def delete_context_endpoint(
    cntxt,
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
 
    return delete_context_param(cntxt,request,response,**kwargs)


#GET DESCENDANTS LINKS

@hug.get("/{cntxt}/descendants")
def get_descendants_param(
    cntxt,
    descendant=None,
    dtype=None,
    label=None,
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

    try:
        out.data=db["context"][cntxt].to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR

    response = out.format(response=response, request=request)

    return


@hug.get("/{cntxt}/descendants/{descendant}")
def get_descendants_endpoint(
    cntxt,
    descendant,
    dtype=None,
    label=None,
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
    return get_descendant_param(cntxt=cntxt,descendant=descendant,dtype=dtype,label=label,request=request,response=response,**kwargs)



# POST DESCENDANTS LINKS

@hug.post("/{cntx}/descendants")
def create_descendants_param(
    cntxt,
    descendant,
    dtype=None,
    label=None,
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
        db["context"][cntxt]={"label":label,"description":description}
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR

    response = out.format(response=response, request=request)

    return

@hug.post("/{cntx}/descendants/{descendant}")
def create_descendants_endpoint(
    cntxt,
    descendant,
    dtype=None,
    label=None,
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

    return create_descendant_param(cntxt=cntxt,descendant=descendant,dtype=dtype,label=label,request=request,response=response,**kwargs)


@hug.delete("/{cntxt}/descendants")
def delete_descendant_param(
    cntxt,
    descendants,
    dtype=None,
    label=None,
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

    try:
        out.data=db["context"].pop(cntxt).to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR

    response = out.format(response=response, request=request)

    return

@hug.delete("/{cntxt}/descendants/{descendant}")
def delete_descendant_endpoint(
    cntxt,
    descendant,
    dtype=None,
    label=None,
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
 
    return delete_descendant_param(cntxt=cntxt,descendant=descendant,dtype=dtype,label=label,request=request,response=response,**kwargs)

 
