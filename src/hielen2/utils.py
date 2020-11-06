#!/usr/bin/env python
# coding=utf-8

from datetime import datetime
from re import split, sub
from time import mktime
import json
from importlib import import_module
from falcon import HTTPNotAcceptable
from hashlib import md5

def hug_output_format_conten_type(handlers=[], error='The requested format does not match any of those allowed', ctpar='content_type'):

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

