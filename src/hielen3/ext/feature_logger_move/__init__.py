# coding=utf-8

__name__ = "feature_logger_move"
__version__ = "0.0.1"
__author__ = "Alessandro Modesti"
__email__ = "it@img-srl.com"
__description__ = "HielenSource extensione"
__license__ = "MIT"
__uri__ = ""


from hielen3.ext.feature_datetree_filesystem_source import loggers
from .logger import Feature, ConfigSchema

__all__ = [ "Feature", "ConfigSchema" ]

