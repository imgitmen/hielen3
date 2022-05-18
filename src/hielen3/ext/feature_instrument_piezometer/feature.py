# coding=utf-8

from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema, PolyCoeff, StringTime
from hielen3.ext.feature_instrument import ConfigSchema, Feature
from marshmallow import fields
import traceback

class ConfigSchema(ActionSchema):
    
    def _self_hints_():

        return {
            "Instruments info":{
                0:["source_series", "Reference raw series", False, None],
                1:["poly", "polinomial coefficients array", False, None],
                2:["head_height", "ground zero", False, None],
                3:["sensor_depth", "sensor distance from the groud zero", False, None],
                4:["timezero", "time of the zero reading", False, None ]
                }
            }

    source_series = fields.String(required=False, allow_none=False)
    poly = PolyCoeff(default=[0,1], required=False, allow_none=True)
    head_height = fields.Number(default=0.0, required=False, allow_none=True)
    sensor_depth = fields.Number(default=0.0, required=False, allow_none=True)
    timezero =  StringTime(required=False, allow_none=True)


class Feature(HFeature):
    '''
    PIEZOMETER
    '''

    def setup(self,**kwargs):
        pass
    
    def config(self, source_series=None, head_height=None, sensor_depth=None, poly=None, timezero=None, **kwargs):

        if not self.parameters.__len__():
            if head_height is None: head_height=0
            if sensor_depth is None: sensor_depth =0
            if poly is None: poly=""
            if timezero is None: zero = 0

        if source_series is not None and poly is not None:
            self.parameters.set(
                    'battente',
                    cache='active',
                    mu="m",
                    modules={"calc":"hielen3.tools.calc"}, 
                    operands={"S0":source_series},
                    operator=f"calc.filter(calc.poly_trans2(S0,{poly}))",
                    first=timezero,
                    ordinal=1
                    )

            contribute=head_height - sensor_depth
            limit=0

            self.parameters.set(
                    'quota falda',
                    cache='active',
                    mu="m.s.l.m.",
                    modules={"calc":"hielen3.tools.calc"},
                    operands={"S0":self.parameters["battente"]},
                    operator=f"calc.add(calc.threshold(S0, limit={limit}, how='<', action='clean'), {contribute})",
                    ordinal=0
                    )

