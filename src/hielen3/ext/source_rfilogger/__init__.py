# coding=utf-8

__name__ = "Source_RfiLogger"
__version__ = "0.0.1"
__author__ = "Alessandro Modesti"
__email__ = "it@img-srl.com"
__description__ = "HielenSource extensione"
__license__ = "MIT"
__uri__ = ""

from .source import Source, ConfigSchema, FeedSchema

__all__ = ["Source", "ConfigSchema", "FeedSchema"]
