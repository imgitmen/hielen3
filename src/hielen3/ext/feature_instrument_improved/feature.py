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
                0:["multi_channel_info_json", "Everything it needs", False, None],
                },

            }

    multi_channel_info_json = fields.String(required=False, allow_none=True)

class SelfParamError(Exception):
    pass

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
            operator=None,
            modules=None,
            coefficients=None,
            timestamp=None,
            start_time=None,
            zero_time=None,
            start_offset=None,
            ordinal=None,
            mu=None,
            valid_range=None,
            view_range=None,
            thresholds=None,
            groupmap=None,
            orient=None
            ):

        print (param_name)

        """
        { 
            "param_name" : "Est"|"Nord"|"Quota",
            "cache" : "old",
            "operands" : FILE_CHANNEL_SERIES,
            "operator" : None,
            "modules"  : {},
            "coefficients" : [0,1000],
            "timestamp" : "ttt",
            "start_time" : None,
            "zero_time" : first,
            "ordinal" : 0 | 1 | 2,
            "mu" | "Δ mm",
            "valid_range : None,
            view_range : [-10,10],
            thresholds : None
        }


        """

        try:
            series=self.parameters[param_name]
        except KeyError as e:
            series=None

        try:
            opz=series.generator.operands
        except Exception as e:
            opz={}

        new_opz={}

        if modules is None:
            modules={}

        if operands is not None:

            for k,w in operands.items():

                if isinstance(w,dict):
                    try:

                        feat=w['feature']

                        if feat == 'self': 

                            feat = self
                        else:
                            try:
                                feat = HFeature.retrive(feat)
                            except Exception as e:
                                raise ValueError (f'error retriving {w}: {feat}')

                        try:
                            w=feat.parameters[w["param"]]

                        except Exception as e:
                            raise SelfParamError(f'error retriving {feat}.{w["param"]}')

                    except KeyError as e:
                        pass

                new_opz[k] = w


        opz.update(new_opz)

        print ("GROUPMAP:",groupmap)

        if groupmap is None:
            opz["Z"] = 0
            opz["OFFSET"] = 0

            if coefficients is None:
                try:
                    coefficients=opz["COEFS"]
                except KeyError as e:
                    coefficients = None

            if coefficients is not None:
                opz["COEFS"] = json.dumps(coefficients)
                modules.update( {"calc":"hielen3.tools.calc"} )
                operator=f"calc.poly_trans2({operator},*COEFS)"


            if start_time is None:
                if zero_time is None or zero_time in ['first']:
                    start_time=timestamp
                else:
                    start_time=zero_time

            if zero_time in ['first']:
                zero_time = start_time

            if operator is not None:
                operator= f"{operator} - Z + OFFSET"


        config=dict(
                param=param_name,
                ordinal=ordinal,
                cache=cache,
                mu=mu,
                modules=modules,
                operands=opz,
                operator=operator,
                first=start_time,
                valid_range=valid_range,
                view_range=view_range,
                thresholds=thresholds,
                groupmap=groupmap,
                orient=orient
                )


        self.parameters.set(**config)

        # ATTENZIONE QUESTA E' UNA FEATURE COMUNE A TUTTE LE SERIE DATI IN DELTA
        if zero_time is not None:
            df=self.parameters[param_name].data(cache='active')

            try:
                df=df.to_frame()
            except Exception as e:
                pass

            df=df[df[df.columns[0]].notna()]

            iloc_idx = df.index.get_indexer([zero_time], method='nearest')

            try:
                config['operands']['Z'] = df.iloc[iloc_idx].squeeze()
            except Exception as e:
                print (f"WARN configuring ZERO for param {param_name}:", e)

        if start_offset is not None:
            try:
                config['operands']['OFFSET'] = start_offset
            except Exception as e:
                print (f"WARN configuring OFFSET for param {param_name}:", e)

        
        if start_offset is not None or zero_time is not None:
            try:
                self.parameters.set(**config)
            except Exception as e:
                print (f"WARN configuring param {param_name}:", e)


    def config(self, multi_channel_info_json=None, timestamp=None,  **kwargs): 

        try:
            infos=json.loads(multi_channel_info_json)
        except Exception as e:
            raise e


        retryinfoslen = 0

        print (self.label,self.uuid)

        while True:
            # Needed to configure self referenced parameters if the dependant
            # parameter comes before the dependency in the info array
            retryinfos=[]

            for info in infos:
                try:
                    self.__channel_config__(timestamp=timestamp,**info)
                except SelfParamError as e:
                    retryinfos.append(info)

            if retryinfos.__len__() == 0:
                return

            if retryinfos.__len__() > 0 and retryinfos.__len__() == retryinfoslen:
                raise ValueError ( f"self parameters reference broken {retryinfos}" )

            retryinfoslen = retryinfos.__len__()

            info = retryinfos.copy()




