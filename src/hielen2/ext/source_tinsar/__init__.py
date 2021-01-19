# coding=utf-8

from hielen2.source import HielenSource


class Source(HielenSource):
    def config(self, **kwargs):
        return kwargs

    def feed(self, **kwargs):
        return kwargs

    def data(self, timefrom=None, timeto=None, geom=None, **kwargs):
        return kwargs
