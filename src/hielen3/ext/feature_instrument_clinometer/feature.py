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
                2:["A_coefficients", "polinomial coefficients array", False, None],
                3:["A_termal_correction","termal correction coefficient", False, None],
                4:["A_start_time", "starting time of the series", False, None],
                5:["A_zero_time", "time of the zero reading", False, None],
                },
            "Channel B": {
                0:["B_param_name", "Label of the axis. i.e.: 'X'", False, None],
                1:["B_source_series", "Reference raw series", False, None],
                2:["B_coefficients", "polinomial coefficients array", False, None],
                3:["B_termal_correction","termal correction coefficient", False, None],
                4:["B_start_time", "starting time of the series", False, None],
                5:["B_zero_time", "time of the zero reading", False, None]
                },
            "Channel C": {
                0:["C_param_name", "Label of the axis. i.e.: 'X'", False, None],
                1:["C_param_series", "Reference raw series", False, None],
                2:["C_coefficients", "polinomial coefficients array", False, None],
                3:["C_termal_correction","termal correction coefficient", False, None],
                4:["C_start_time", "starting time of the series", False, None],
                5:["C_zero_time", "time of the zero reading", False, None]
                },
            "Channel Temp": {
                0:["T_source_series", "Reference raw series", False, None],
                1:["T_zero_time", "time of the zero reading", False, None]
                },

            }

    A_param_name = fields.String(required=False, allow_none=True)
    A_source_series = fields.String(required=False, allow_none=True)
    A_coefficients = PolyCoeff(default=[0,1], required=False, allow_none=True)
    A_termal_correction = fields.Number(default=1, required=False, allow_none=True)
    A_start_time =  StringTime(required=False, allow_none=True)
    A_zero_time =  StringTime(required=False, allow_none=True)

    B_param_name = fields.String(required=False, allow_none=True)
    B_source_series = fields.String(required=False, allow_none=True)
    B_coefficients = PolyCoeff(default=[0,1], required=False, allow_none=True)
    B_termal_correction = fields.Number(default=1, required=False, allow_none=True)
    B_start_time =  StringTime(required=False, allow_none=True)
    B_zero_time =  StringTime(required=False, allow_none=True)

    C_param_name = fields.String(required=False, allow_none=True)
    C_source_series = fields.String(required=False, allow_none=True)
    C_coefficients = PolyCoeff(default=[0,1], required=False, allow_none=True)
    C_termal_correction = fields.Number(default=1, required=False, allow_none=True)
    C_start_time =  StringTime(required=False, allow_none=True)
    C_zero_time =  StringTime(required=False, allow_none=True)

    T_source_series = fields.String(required=False, allow_none=True)
    T_start_time =  StringTime(required=False, allow_none=True)


class Feature(HFeature):
    '''
    CLINOMETER
    '''

    def setup(self,**kwargs):
        pass
    
    def __channel_config__(
            self, 
            ch, 
            param_name,
            source_series=None,
            temp_series=None,
            termal_correction=None,
            coefficients=None,
            start_time=None,
            zero_time=None,
            ordinal=None ):


        # DA RIVEDERE IL MECCANISMO DI CONSISTENZA TRA UNA CONF E L'ALTRA
        try:
            old_source_series = self.parameters[param_name].uuid
        except KeyError as e:
            old_source_series = None
        
        if  old_source_series is None:
            if coefficients is None: coefficients=""

        if temp_series is None:
            temp_series=0

        if termal_correction is None:
            termal_correction=0

        if source_series is None:
            source_series = old_source_series

        if source_series is not None:

            config=dict(
                    param=param_name,
                    ordinal=ordinal,
                    cache="active",
                    mu="Δ mm/m",
                    modules={"calc":"hielen3.tools.calc"},
                    operands={"S0":source_series, "T0":temp_series},
                    operator=f"calc.filter(calc.poly_trans2(S0,{coefficients})*1000 + T0 * {termal_correction})",
                    first=start_time
                    )

            self.parameters.set(**config)

            # ATTENZIONE QUESTA E' UNA FEATURE COMUNE A TUTTE LE SERIRE DATI IN DELTA
            if zero_time is not None:
                df=self.parameters[param_name].data()
                iloc_idx = df.index.get_indexer([zero_time], method='nearest')
                ZERO = df.iloc[iloc_idx].squeeze()
                config["operator"] += f" - {ZERO}"
                self.parameters.set(**config)



    def config(self, **kwargs):

        tkwargs={
                "A_param_name":None,
                "A_source_series":None,
                "A_coefficients":None,
                "A_termal_correction":None,
                "A_start_time":None,
                "A_zero_time":None,
                "B_param_name":None,
                "B_source_series":None,
                "B_coefficients":None,
                "B_termal_correction":None,
                "B_start_time":None,
                "B_zero_time":None,
                "C_param_name":None,
                "C_source_series":None,
                "C_coefficients":None,
                "C_termal_correction":None,
                "C_start_time":None,
                "C_zero_time":None,
                "T_source_series":None,
                "T_zero_time":None
                }


        tkwargs.update(kwargs)

        
        A = { "_".join(k.split("_")[1:]):w for k,w in tkwargs.items() if k[0] == "A" }
        B = { "_".join(k.split("_")[1:]):w for k,w in tkwargs.items() if k[0] == "B" }
        C = { "_".join(k.split("_")[1:]):w for k,w in tkwargs.items() if k[0] == "C" }
        T = { "_".join(k.split("_")[1:]):w for k,w in tkwargs.items() if k[0] == "T" }
        
        try:
            timestamp = kwargs["timestamp"]
        except KeyError as e:
            timestamp = None

        if A["start_time"] is None: A["start_time"] = timestamp
        if B["start_time"] is None: B["start_time"] = timestamp
        if C["start_time"] is None: C["start_time"] = timestamp
        if T["start_time"] is None: T["start_time"] = timestamp

        if A["zero_time"] is None: A["zero_time"] = A["start_time"]
        if B["zero_time"] is None: B["zero_time"] = B["start_time"]
        if C["zero_time"] is None: C["zero_time"] = C["start_time"]

        self.parameters.set(
                    "Temperatura",
                    cache="no",
                    mu="*C",
                    modules={},
                    operands={"S0":T["source_series"]},
                    operator="S0",
                    first=T["start_time"],
                    ordinal=3
                    )

        temperature=self.parameters["Temperatura"]

        self.__channel_config__(ch="A",ordinal=0,temp_series=temperature,**A)

        self.__channel_config__(ch="B",ordinal=1,temp_series=temperature,**B)

        self.__channel_config__(ch="C",ordinal=2,temp_series=temperature,**C)


