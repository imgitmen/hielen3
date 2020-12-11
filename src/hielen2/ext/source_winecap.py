# coding: utf-8
from pandas import DataFrame, Series, to_datetime
from zeep import Client
from zeep.helpers import serialize_object
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from time import time
from hielen.utils import isot2ut

"""

sudo apt-get install libxml2-dev libxslt1-dev

pip install lxml==4.2.5 zeep

"""


# key='80d373db820fea6f8c5f57d125eb509d'
key = "04a71268d386d61801824863ad7e2a5d"
GWOmac = "00009DEA"


def get_ch(GW=None, LG=None, CH=None, timefrom=None, timeto=None):
    return GWO(mac=GW).getDataSeries(mac=LG, ch=CH, timefrom=timefrom, timeto=timeto)


def threadpool(f, executor=None):
    @wraps(f)
    def wrap(*args, **kwargs):
        return ThreadPoolExecutor().submit(f, *args, **kwargs)

    return wrap


class GWO:
    def __init__(
        self, key=key, mac=GWOmac, wsdl="http://www.winecap.it/winecapws.wsdl"
    ):
        self.key = key
        self.mac = mac
        self.client = Client(wsdl=wsdl)
        self._gch = self.client.service.getChannelHistory
        self._gsh = self.client.service.getSystemHistory
        self._gsl = self.client.service.getSensorList

    def getSensorsList(self):
        return DataFrame(serialize_object(self._gsl(self.key, self.mac)))

    def getDataSeries(self, mac, ch, timefrom=None, timeto=None):

        if not isinstance(timefrom, int):
            timefrom = isot2ut(timefrom)

        if timeto is None:
            timeto = int(time())

        if not isinstance(timeto, int):
            timeto = isot2ut(timeto)

        ahead = True
        out = Series()

        while ahead:

            u = DataFrame(
                serialize_object(
                    self._gch(self.key, self.mac, mac, ch, timefrom, timeto)
                )
            )

            if u.__len__() < 1024:
                ahead = False

            if u.__len__() > 0:
                u = u.set_index(["timeStamp"])["value"]
                u.index.names = ["timestamp"]
                timefrom = u.index.max() + 1
                out = out.append(u)

        out = out.sort_index()
        out.name = f"{mac}_{ch}"
        out.sort_index()
        out.index = to_datetime(out.index, unit="s")

        return out

    @threadpool
    def getThreadedSeries(self, *args, **kwargs):
        return self.getDataSeries(*args, **kwargs)

    def getDataFrame(self, reqser=[], timefrom=None, timeto=None):
        thds = [self.getThreadedSeries(*x, timefrom, timeto) for x in reqser]
        return [x.result() for x in thds]

    def getDataFrameSE(self, reqser=[], timefrom=None, timeto=None):
        return [self.getDataSeries(*x, timefrom, timeto) for x in reqser]
