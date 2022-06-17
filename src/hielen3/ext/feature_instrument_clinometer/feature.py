# coding=utf-8

from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema, PolyCoeff, StringTime
from hielen3.ext.feature_instrument import ConfigSchema, Feature
from marshmallow import fields
import traceback

class ConfigSchema(ActionSchema):
    
    def _self_hints_():

        return {
            "Channel A": {
                0:["A_param_name", "Label of the axis. i.e.: 'X'", False, None],
                1:["A_source_series", "Reference raw series", False, None],
                2:["A_coefficents", "polinomial coefficients array", False, None],
                3:["A_timezero", "time of the zero reading", False, None ],
                },
            "Channel B": {
                0:["B_param_name", "Label of the axis. i.e.: 'X'", False, None],
                1:["B_source_series", "Reference raw series", False, None],
                2:["B_coefficents", "polinomial coefficients array", False, None],
                3:["B_timezero", "time of the zero reading", False, None ]
                },
            "Channel C": {
                0:["C_param_name", "Label of the axis. i.e.: 'X'", False, None],
                1:["C_param_series", "Reference raw series", False, None],
                2:["C_coefficents", "polinomial coefficients array", False, None],
                3:["C_timezero", "time of the zero reading", False, None ]
                },
            "Channel Temp": {
                0:["T_param_name", "Label of the axis. i.e.: 'X'", False, None],
                1:["T_source_series", "Reference raw series", False, None],
                2:["T_coefficents", "polinomial coefficients array", False, None],
                3:["T_timezero", "time of the zero reading", False, None ]
                },

            }

    A_param_name = fields.String(required=False, allow_none=False)
    A_source_series = fields.String(required=False, allow_none=False)
    A_poly = PolyCoeff(default=[0,1], required=False, allow_none=True)
    A_timezero =  StringTime(required=False, allow_none=True)

    B_param_name = fields.String(required=False, allow_none=False)
    B_source_series = fields.String(required=False, allow_none=False)
    B_poly = PolyCoeff(default=[0,1], required=False, allow_none=True)
    B_timezero =  StringTime(required=False, allow_none=True)

    C_param_name = fields.String(required=False, allow_none=False)
    C_source_series = fields.String(required=False, allow_none=False)
    C_poly = PolyCoeff(default=[0,1], required=False, allow_none=True)
    C_timezero =  StringTime(required=False, allow_none=True)

    T_param_name = fields.String(required=False, allow_none=False)
    T_source_series = fields.String(required=False, allow_none=False)
    T_poly = PolyCoeff(default=[0,1], required=False, allow_none=True)
    T_timezero =  StringTime(required=False, allow_none=True)


class Feature(HFeature):
    '''
    CLINOMETER
    '''

    def setup(self,**kwargs):
        pass
    
    def __channel_config__(self, ch, param_name, source_series=None, poly=None, timezero=None, ordinal=None, timestamp=None):

        try:
            oldinfo=self.parameters[param_name]
        except KeyError as e:
            oldinfo = None
        
        if  oldinfo is None:
            if poly is None: poly=""
            if timezero is None: timezero = timestamp

        if ch in ["A","B","C"]:
            mu="mm/m"
            modules={"calc":"hielen3.tools.calc"},
            operands={"S0":source_series},
            operator=f"calc.filter(calc.poly_trans2(S0,{poly})*1000)"
        else: 
            mu = "\°C",
            modules=None,
            operands=None,
            operator=None

        if source_series is not None and poly is not None:
            self.parameters.set(
                    param_name,
                    cache='active',
                    mu=mu,
                    modules=modules,
                    operands=operands,
                    operator=operator,
                    first=timezero,
                    ordinal=ordinal
                    )


    def config(self, **kwargs):

        tkwargs={
                "A_param_name":None,
                "A_source_series":None,
                "A_poly":None,
                "A_timezero":None,
                "B_param_name":None,
                "B_source_series":None,
                "B_poly":None,
                "B_timezero":None,
                "C_param_name":None,
                "C_source_series":None,
                "C_poly":None,
                "C_timezero":None,
                "T_param_name":None,
                "T_source_series":None,
                "T_poly":None,
                "T_timezero":None,
                }


        tkwargs.update(kwargs)

        info_ch={
                "A": { "_".join(k.split("_")[1:]):w for k,w in tkwargs.items() if k[0] == "A" },
                "B": { "_".join(k.split("_")[1:]):w for k,w in tkwargs.items() if k[0] == "B" },
                "C": { "_".join(k.split("_")[1:]):w for k,w in tkwargs.items() if k[0] == "C" },
                "T": { "_".join(k.split("_")[1:]):w for k,w in tkwargs.items() if k[0] == "T" }
                }

        try:
            timestamp = kwargs["timestamp"]
        except KeyError as e:
            timestamp = None

        if info_ch["A"].__len__():
            self.__channel_config__(ch="A",timestamp=timestamp,ordinal=0,**info_ch["A"])

        if info_ch["B"].__len__():
            self.__channel_config__(ch="B",timestamp=timestamp,ordinal=1,**info_ch["B"])

        if info_ch["C"].__len__():
            self.__channel_config__(ch="C",timestamp=timestamp,ordinal=2,**info_ch["C"])

        if info_ch["T"].__len__():
            self.__channel_config__(ch="T",timestamp=timestamp,ordinal=4,**info_ch["T"])

