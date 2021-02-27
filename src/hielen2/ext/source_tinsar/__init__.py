# coding=utf-8

from hielen2.source import HielenSource
from hielen2.source import HielenSource, ActionSchema
from hielen2.utils import LocalFile
from marshmallow import fields


class ConfigSchema(ActionSchema):
    master_cloud = LocalFile(required=True, allow_none=False)
    geo_reference_file = LocalFile(required=False, default=None, allow_none=True)
    crs=fields.Str(required=False,default=None,allow_none=True)

class FeedSchema(ActionSchema):
    scanner_file=LocalFile(required=True, allow_none=False)


class Source(HielenSource):
    def config(self, **kwargs):
        return kwargs

    def feed(self, **kwargs):
        return kwargs

    def data(self, timefrom=None, timeto=None, geom=None, **kwargs):
        return kwargs
