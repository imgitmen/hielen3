# coding=utf-8

__name__ = 'hielen3'
__version__ = '3.3.6'
__author__ = 'Alessandro Modesti'
__email__ = 'it@img-srl.com'
__description__ = 'Multidimention Hierarichical Elaboration Engine'
__license__ = 'MIT'
__uri__ = ''

import warnings
import json

from .datalink import dbinit  # , cacheinit


def _initconf(confile, envfile):
    env = None
    with open(envfile) as ef:
        env = json.load(ef)

    with open(confile) as cf:
        confstr = cf.read()
        for k, w in env.items():
            if not isinstance(w,str):
                w=json.dumps(w)
            placeholder = "{{" + k + "}}"
            confstr = confstr.replace(placeholder, w)

    return json.loads(confstr)


conf = _initconf("./conf/hielen.json", "./conf/env.json")

db = dbinit(conf)

def int_or_str(value):
    try:
        return int(value)
    except ValueError:
        return value


VERSION = tuple(map(int_or_str, __version__.split(".")))

__all__ = ["conf", "db"]
