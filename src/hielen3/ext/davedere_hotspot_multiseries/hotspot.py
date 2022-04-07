# coding=utf-8

"""
from hielen3.source import ActionSchema, DataSource 
from hielen3.utils import LoggerHeader
from pandas import read_csv, DatetimeIndex, Series
"""
from marshmallow import fields
from pathlib import Path
#import hielen3.tools.calc as calc
import traceback


class ConfigSchema(ActionSchema):
    pass
    
    """
    _self_hints={
            "Logger info": {
                0:["logger_type","The logger type"],
                1:["logger_serial", "The logger serial"],
                2:["logger_header", "The logger header"]
                }
            }

    logger_type = fields.Str(required=True, allow_none=False)
    logger_serial = fields.Str(reuired=True, allow_none=False)
    logger_header = LoggerHeader(required=False,allow_none=True,default=None)
    """



class Source(DataSource):
    '''
    RawSourceData manager
    '''

    pass
    '''
    def config(self, **kwargs):


        chlist=kwargs['logger_header']
        logger=kwargs['logger_serial']
        logger_type=kwargs['logger_type']

        if  chlist is None:
            chlist=[]

           
        """
        param:0
        column:1
        raw_mu:2
        ing_mu:3
        signal_cond:4
        poli_coeff:5
        """

        for chinfo in chlist:

            operands={
                "param":chinfo[0],
                "column": chinfo[1],
                "rawunit": chinfo[2],
                "logger":logger,
                "logger_type":logger_type
                }

            if isinstance(chinfo[5],list):
                for p in range(chinfo[5].__len__()):
                    operands.update( { f"E{p}" : chinfo[5][p] }  )

            chstruct={
                "param": chinfo[0],
                "struct": {
                    "cache": "active",
                    "modules": {},
                    "mu":chinfo[3],
                    "operands":operands,
                    "operator": None
                    }
                }

            self.addParamSeries(**chstruct)


        return kwargs


    def cleanConfig(self,timestamp):
        pass


    def data( 
            self,
            logger_type=None,
            logger=None,
            param=None,
            column=None,
            rawunit=None,
            times=None,
            filename="last_load.csv", 
            **kwargs ):

        if times is None:
            times = slice(None,None,None)

        if column is None:
            column = 0

        incomes=Path(self.incomepath,logger_type,logger,filename)

        try:
            out = read_csv(
                str( incomes ),
                header=None,
                index_col=[0],
                parse_dates=True
            )

            out=out[out.columns[column]].squeeze()

            out = calc.poly_trans(out, **kwargs) 

            scalar=param.split("_")[0]

            if scalar in ['rot']:
                out = calc.slope(out,rawunit,1)

        except Exception as e:
            traceback.print_exc()
            return Series()


        #out = out[columns]


        # out.columns=[self.uid]
        # out.index=to_datetime(out.index)
        return out.loc[times]
'''
