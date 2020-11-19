#!/usr/bin/env python
# coding=utf-8
from abc import ABC,abstractmethod

class Source(ABC):

    @abstractmethod
    def config():
        pass

    @abratactmethod
    def feed():
        pass

    @abstractmethod
    def series():
        pass

    @abstractmethod
    def maps():
        pass

    @abstractmethod
    def cloud():
        pass
