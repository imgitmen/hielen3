# coding=utf-8

from hielen3.feature import HFeature
from hielen3.serializaction import ActionSchema, PolyCoeff, StringTime
from hielen3.ext.feature_instrument import ConfigSchema, Feature
from marshmallow import fields

import json
import traceback

class ConfigSchema(ActionSchema):
    
    def _self_hints_():

        return {
            "Channels Info": {
                0:["multi_channel_info_json", "Every things it needs", False, None],
                },

            }

    multi_channel_info_json = fields.String(required=False, allow_none=True)


class Feature(HFeature):
    '''
    INSTRUMENT
    '''

    def setup(self,**kwargs):
        pass
    
    def __channel_config__(
            self, 
            param_name,
            source_series=None,
            source_label=None,
            source_parameter=None,
            coefficients=None,
            timestamp=None,
            start_time=None,
            zero_time=None,
            ordinal=None,
            unit=None,
            valid_range=None,
            view_range=None,
            thresholds=None
            ):


        if start_time is None:
            if zero_time is None:
                start_time=timestamp
            else:
                start_time=zero_time

        # DA RIVEDERE IL MECCANISMO DI CONSISTENZA TRA UNA CONF E L'ALTRA
        try:
            old_source_series = self.parameters[param_name].uuid
        except KeyError as e:
            old_source_series = None
        
        if coefficients is not None:
            coefficients = ",".join(map(str,coefficients))

        if  old_source_series is None:
            if coefficients is None: coefficients=""

        if source_label is not None and source_parameter is not None:
            try:
                source_series = HFeature.retrive_label(source_label).parameters[source_parameter]
            except Exception as e:
                print (e)
                pass

        if source_series is None:
            source_series = old_source_series

        if source_series is not None:

            """ porcata per velocizzare valle ragone"""

            if self.label[0] in ("T", "F"):
                operator=f"calc.poly_trans2({coefficents})"

            elif self.label[0] == "C":
                operator=f"calc.filter(calc.slope(calc.poly_trans2(S0,{coefficients}),radius=1000), 2, 10)"

            else:
                operator=None

            """ fine porcata """

            config=dict(
                    param=param_name,
                    ordinal=ordinal,
                    cache="active",
                    mu=unit,
                    modules={"calc":"hielen3.tools.calc"},
                    operands={"S0":source_series},
                    operator=operator,
                    first=start_time,
                    valid_range=valid_range,
                    view_range=view_range,
                    thresholds=thresholds
                    )

            self.parameters.set(**config)

            # ATTENZIONE QUESTA E' UNA FEATURE COMUNE A TUTTE LE SERIE DATI IN DELTA
            if zero_time is not None:
                df=self.parameters[param_name].data()
                iloc_idx = df.index.get_indexer([zero_time], method='nearest')
                try:
                    ZERO = df.iloc[iloc_idx].squeeze()
                except Exception as e:
                    ZERO=0

                config["operator"] += f" - {ZERO}"
                self.parameters.set(**config)



    def config(self, multi_channel_info_json=None, timestamp=None,  **kwargs): 

        try:
            infos=json.loads(multi_channel_info_json)
        except Exception as e:
            raise e

        for info in infos:
            self.__channel_config__(timestamp=timestamp,**info)

