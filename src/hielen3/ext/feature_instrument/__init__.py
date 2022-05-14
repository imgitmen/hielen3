# coding=utf-8

__name__ = "Feature_instrument"
__version__ = "0.0.1"
__author__ = "Alessandro Modesti"
__email__ = "it@img-srl.com"
__description__ = "HielenSource extensione"
__license__ = "MIT"
__uri__ = ""

from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema as ConfigSchema


class Feature(HFeature):

    '''
    Default Feature
    '''

    def setup(self,*args,**kwargs):
        pass

    def config(self,*args,**kwargs):
        pass



__all__ = ["Feature","ConfigSchema","__all__"]
