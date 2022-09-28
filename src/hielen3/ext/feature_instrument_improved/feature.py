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
            cache=None,
            operands=None,
            modules=None,
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

        try:
            series=self.parameters[param_name]
        except KeyError as e:
            series=None

        try:
            opz=series.generator.operands
        except Exception as e:
            opz={}

        new_opz={}

        if operands is not None:
            for k,w in operands:

                wtype=w["type"]
                winfo=w["info"]
                feat=self

                ## MI ASPETTO QUESTO:
                """
                {
                    "type": "value" |  "series_uuid" | "feature_param"
                    "info": "uuid" | {"feature":"feature_uuid_name_null","param":"param_name"} | value 
                }

                """

                ## RESOLVING feature_param serie and set winfo with that
                if wtype ==  "feature_param" :
                    if winfo["feature"] is not None:
                        feat = HFeature.retrive(winfo["feature"])
                    winfo=feat.parameters[winfo[param]]

                new_opz[k] = winfo

        opz.update(new_opz)

        opz["Z"] = 0

        if coefficients is None:
            try 
                coefficients=opz["COEFS"]
            except KeyError as e:
                coefficients=[]

        opz["COEFS"] = coefficients

        if start_time is None:
            if zero_time is None:
                start_time=timestamp
            else:
                start_time=zero_time

        if operator is not None:
            operator= f"operator - Z"


        config=dict(
                param=param_name,
                ordinal=ordinal,
                cache=cache,
                mu=unit,
                modules=modules,
                operands=opz,
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
                    config['operands']['Z'] = df.iloc[iloc_idx].squeeze()
                    self.parameters.set(**config)
                except Exception as e:
                    pass


    def config(self, multi_channel_info_json=None, timestamp=None,  **kwargs): 

        try:
            infos=json.loads(multi_channel_info_json)
        except Exception as e:
            raise e

        for info in infos:
            self.__channel_config__(timestamp=timestamp,**info)

