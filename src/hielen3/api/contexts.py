#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3 import db
from hielen3.utils import ResponseFormatter
from hielen3.utils import clean_input
from hielen3.contextmanager import lineages
from hielen3.contextmanager import ancestors

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

    cntxt=clean_input(cntxt)

    try:
        out.data=db["context"][cntxt].to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

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

    cntxt=clean_input(cntxt)

    try:
        db["context"][cntxt]={"label":label,"description":description}
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

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

    cntxt=clean_input(cntxt)

    try:
        out.data=db["context"].pop(cntxt).to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

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

    cntxt=clean_input(cntxt)

    descendant = clean_input(descendant)

    try:

        out.data=[ c for c in lineage(cntxt) if descendant is None or c in descendant  ]
    
    except ValueError as e:
        out.message = "Context is None: "+str(e)
!       out.status = falcon.HTTP_CONFLICT

    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

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
    homogeneous=None,
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

    cntxt=clean_input(cntxt)
    
    descendant = clean_input(descendant)
    dtype = clean_input(dtype,trim_none=False)
    label = clean_input(label,trim_none=False)
    homogeneous = clean_input(homogeneous,trim_none=False)
    
    try:
        if cntxt is None:
            raise Exception ( "cntxt required" )
        if cntxt.__len__() > 1:
            raise Exception ( "cntxt must be exactly one" )
        if descendant is None:
            raise Exception ( "descendant required" )

        if dtype is not None and dtype.__len__() > 1 and dtype.__len__() != descendant.__len__():
            raise ValueError ("dtype length invalid")

        if label is not None and label.__len__() > 1 and label.__len__() != descendant.__len__():
            raise ValueError ("label length invalid")

        if homogeneous is not None and homogeneous.__len__() > 1 and homogeneous.__len__() != descendant.__len__():
            raise ValueError ("homogeneous length invalid")

        if dtype is not None and dtype.__len__() == 1:
            v = dtype[0]
            dtype=[ v for a in descendant ]
    

        if label is not None and label.__len__() == 1:
            v = label[0]
            label=[ v for a in descendant ]
   

        if homogeneous is not None and homogeneous.__len__() == 1:
            v = homogeneous[0]
            homogeneous=[ v for a in descendant ]

        homogeneous=map( lambda x: int(x is None) or x, homogeneous)

        for i in descendants:
            db["context_context"][{"ancestor":cntxt,"descendant":descendant[i]}]={"label":label[i],"homogeneous":homogeneous[i],"klass":dtype[i]}

    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

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
        out.status = falcon.HTTP_CONFLICT

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

 
