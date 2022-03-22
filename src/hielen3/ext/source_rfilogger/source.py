# coding=utf-8

from hielen3.source import ActionSchema, DataSource 
from hielen3.utils import ParamsDefinition, LocalFile
from pandas import read_csv, DatetimeIndex, Series, DataFrame
from marshmallow import fields
from pathlib import Path
from numpy import unique
import hielen3.tools.calc as calc
import traceback


class ConfigSchema(ActionSchema):
    
    _self_hints={
            "Raw Source info": {
                0:["param_list", "list of parameters",False]
                }
            }

    param_list = ParamsDefinition(required=False,allow_none=True,default=None)


class FeedSchema(ActionSchema):

    _self_hints = {
              "Raw Source Feed": {
                  0:["input_file", "input file to load",False],
                  1:["separator", "CSV field separator",False]
                  },
          }

    input_file = LocalFile(required=False, allow_none=True)


class Source(DataSource):
    '''
    RawSourceData manager
    '''

    @property
    def incomesfile(self):
        return self.filecache / 'last_load.csv'


    def config(self, **kwargs):

        self.filecache.mkdir()

        chlist=kwargs['param_list']


        if  chlist is None:
            chlist=[]

           
        """
        param:0
        column:1
        ing_mu:2
        """

        for chinfo in chlist:

            chstruct={
                "param": chinfo[0],
                "struct": {
                    "cache": "active",
                    "modules": {},
                    "mu":chinfo[2],
                    "operands": {
                        "column":chinfo[1]
                        },
                    "operator": None
                    }
                }

            self.addParamSeries(**chstruct)


        return kwargs



    def cleanConfig(self,timestamp):
        self.cleanFeatureCache()
        self.filecache.rmdir()


    def feed(self, **kwargs):

        _input_=kwargs['input_file']

        incomes=DataFrame([])

        if _input_ is not None:

            #try if is a file


            if isinstance(_input_, str ):

                try:
                    incomes=read_csv(
                            str( _input_ ),
                            header=None,
                            index_col=[0],
                            parse_dates=True,
                            sep=","
                            )

                except Exception as e:
                   #traceback.print_exc()
                   pass

            if isinstance(_input_, (DataFrame,Series)):
                incomes=_input_

            if not incomes.empty:
                loaded=self.data()

                try:
                    loaded = loaded.to_frame()
                except Exception as e:
                    #traceback.print_exc()
                    pass

                try:
                    incomes = incomes.to_frame()
                except Exception as e:
                    #traceback.print_exc()
                    pass

                #IT COULD RAISE AN EXCEPTION IF COLUMNS NUMBERS DO NOT MATCH
                if loaded.empty:
                    loaded=incomes
                else:
                    incomes.columns=loaded.columns
                    loaded=loaded.append(incomes).sort_index()
                    idx = unique(loaded.index.values, return_index=True)[1]
                    loaded = loaded.iloc[idx]
                

                if not loaded.empty:
                    loaded.to_csv(self.incomesfile,header=None,sep=",")

        return kwargs


    def cleanFeed(self,timestamp):
        pass


    def data( 
            self,
            times=None,
            column=None,
            **kwargs ):


        if times is None:
            times=slice(None,None,None)

        loaded=self.incomesfile

        try:
            out = read_csv(
                str( loaded ),
                header=None,
                index_col=[0],
                parse_dates=True,
                sep=","
            )
            
            if column is not None:
                out=out[out.columns[column]]

            out=out.squeeze()

        except Exception as e:
            #traceback.print_exc()
            return Series()

        print (times)

        # out.columns=[self.uid]
        # out.index=to_datetime(out.index)
        return out.loc[times]

