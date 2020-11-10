#!/usr/bin/env python
# coding=utf-8

from datetime import datetime
from re import split, sub, findall
from time import mktime
import json
from importlib import import_module
from falcon import HTTPNotAcceptable
from hashlib import md5
from marshmallow import Schema, fields

def hug_output_format_conten_type(handlers=[], 
        error='The requested format does not match any of those allowed', ctpar='content_type'):

    """Returns a different handler depending on the input param ctpar
    If none match and no default is given falcon.HTTPNotAcceptable(error)
    is raised
    """

    try:
        default=handlers[0]
    except Exception:
        default=None

    handlers={ h.content_type:h for h in handlers }

    def requested_output_type(request=None):
        try:
            par=request._params[ctpar]
            handler=None

            for k,h in handlers.items():
                if par.split(';')[0] == k.split(';')[0]:
                    handler=h
                    break

        except Exception:
            if default is not None:
                handler = default

        if handler is None:
            raise HTTPNotAcceptable(error)

        return handler

    def output_type(data, request, response):
        handler=requested_output_type(request)
        response.content_type = handler.content_type
        return handler(data, request=request, response=response)

    output_type.__doc__ = "Supports any of the following formats: {0}".format(", ".join(function.__doc__ for function in handlers.values()))
    output_type.content_type = ", ".join(handlers.keys())
    output_type.requested = requested_output_type

    return output_type


def newinstanceof(klass,*args,**kwargs):

    klass_ar=klass.split('.')
    module='.'.join(klass_ar[:-1])
    klass=klass_ar[-1]

    return getattr(import_module(module),klass)(*args,**kwargs)


def ut2isot(u=None):
     u = u or 1
     return str(datetime.fromtimestamp(u))


def isot2ut(t=None):

    t = t or "1970-01-01T01:00:01.00000Z"

    dt = datetime( *map(int,split('[^\d]', sub('[^\d]$','',t))))
    return int(mktime(dt.timetuple()))


def loadjsonfile(filename):
    with open(filename) as jf:
        return json.load(jf)


def savejsonfile(filename,struct):
    with open(filename,'w') as jf:
        json.dump(struct,jf)

def eprint(*args, fname='error', **kwargs):
    with open(fname,'a') as f:
        print (*args,file=f,**kwargs)

def hashfile(filename):
    BLOCKSIZE = 65536
    hasher = md5()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


class JsonValidable():
    """
    JSON Validator class.
    It is initailzed with a marshmallow.Schema instance. When __call__ function is invoked, \
    uses marshmallow facilities to validate the json and raise errors.

    Once initalized, changes __doc__ in order to descibe the json accepted.
    """

    def __field_doc__(self,field):
        types=""
        required=field.required and "*" or ""
        try:
            types="|".join(self.TYPE_MAPPING[field.__class__])
        except KeyError:
            if field.__class__ is  fields.List:
                f,required=self.__field_doc__(field.inner)
                types=f"[{f}]"
            elif field.__class__ is fields.Dict:
                kf,required=self.__field_doc__(field.key_field)
                vf,required=self.__field_doc__(field.value_field)
                types=f"{{{kf},{vf}}}"

        return (types,required)

 
    def __schema_doc__(self):
        flds=[]
        for n,f in self.schema.fields.items():
            types,required=self.__field_doc__(f)
            flds.append( f"**{n}**{required}: {types}")
        fields=", ".join( flds )
        fields=f"{{{fields}}}"
        if self.schema.many:
            fields=f"[{fields}]"
        return f"JSON Schema {fields}"

    
    def __init__(self,schema):
        self.schema = schema
        self.TYPE_MAPPING={}
        for k,w in self.schema.TYPE_MAPPING.items():
            try:
                self.TYPE_MAPPING[w].append(findall(r"'(.*)'",str(k))[0])
            except KeyError:
                self.TYPE_MAPPING[w]=[findall(r"'(.*)'",str(k))[0]]
        self.__doc__ = str(self.__schema_doc__())


    def __call__(self,value):
    
        if type(value) is list:
            # If Falcon is set to comma-separate entries, this segment joins them again.
            fixed_value = ",".join(value)
        else:
            fixed_value = value

        return self.schema.loads(fixed_value)



