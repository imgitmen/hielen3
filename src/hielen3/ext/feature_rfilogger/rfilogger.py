# coding=utf-8

from hielen3 import conf
from hielen3.feature import HFeature
from hielen3.series import HSeries
from hielen3.serializaction import ActionSchema, FTPPath, PolyCoeff, LoggerHeader
from marshmallow import fields
#from pandas import read_csv, DatetimeIndex, Series, DataFrame
from pathlib import Path 
import traceback

from glob import glob
from pathlib import Path
from pandas import Series, DataFrame, read_csv, concat
from datetime import datetime

def logger_serials(folder='gestecno_rfi/data'):

    folder=Path( conf['incomepath']) / folder / "*"

    serials=Series(glob(str(folder)),dtype='object').apply(Path)

    serials=serials[serials.apply(Path.is_dir)]

    return list(serials.apply(lambda x: x.name).sort_values().values )


class ConfigSchema(ActionSchema):
    
    def _self_hints_():

        return {
                "Logger info": {
                0:["serial", "Logger serial number", False, logger_serials()]
                },
            "Instruments info":{
                0:["radar_1", "Radar 1 polynomial coefficients", False, None],
                1:["radar_2", "Radar 2 polynomial coefficients", False, None],
                2:["pluviometer", "Pluviometer polynomial coefficients", False, None],
                3:["h_radar_1", "Quote over sea level of the radar 1", False, None],
                4:["h_radar_2", "Quote over sea level of the radar 2", False, None],
                5:["h_min_span_1", "Quote over the sea level of the minimum free span", False, None]
                6:["h_min_span_2", "Quote over the sea levle of the minimum free span", False, None]
                }
            }

    serial = fields.String(required=True, allow_none=False)
    radar_1 = PolyCoeff(default=[0,1], required=False, allow_none=True)
    radar_2 = PolyCoeff(default=[0,1], required=False, allow_none=True)
    pluviometer = PolyCoeff(default=[0,0.2], reqired=False, allow_none=True)
    h_radar_1 = fields.Number(required=True, allow_none=True)
    h_radar_2 = fields.Number(required=True, allow_none=True)
    h_min_span_1 = fields.Number(required=True, allow_none=True)
    h_min_span_2 = fields.Number(required=True, allow_none=True)



class Feature(HFeature):
    '''
    RfiLogger
    '''

    def setup(self,**kwargs):
        pass
    
    def config(
            self,
            serial,
            radar_1=None,
            radar_2=None,
            pluviometer=None,
            h_radar_1=None,
            h_radar_2=None,
            h_min_span_1=None,
            h_min_span_2=None,
            **kwargs):

        """
        Timestamp,
        0:Alarm,
        1:Temp_°C,
        2:Humid_%,
        3:ADC 0_V,
        4:lev1_m,
        5:lev2_m,
        6:pio1
        """

        source=str(self.__module__)

        try:
            timestamp = kwargs["timestamp"]
        except KeyError as e:
            timestamp = None

        if not self.parameters.__len__():
            if radar_1 is None: radar_1=""
            if radar_2 is None: radar_2=""
            if h_radar_1 is None: h_radar_1=0
            if h_radar_2 is None: h_radar_2=0
            if h_min_span_1 is None: h_min_span_1=0
            if h_min_span_2 is None: h_min_span_2=0


        self.parameters.set(
                "camera",
                cache='inactive',
                ordinal=100,
                modules={"hls": "hielen3.tools.hls_facility"},
                operator=f"hls.start_stream(resource={serial!r})",
                capability="stream")

        self.parameters.set(
                "temperature",
                cache='active',
                mu='°C',
                ordinal=8,
                first=timestamp,
                modules={"source":source},
                operator=f"source.retrive(serials={serial!r},times=times,columns=2)")

        self.parameters.set(
                "humidity",
                cache='active',
                mu='%%',
                ordinal=9,
                first=timestamp,
                modules={"source":source},
                operator=f"source.retrive(serials={serial!r},times=times,columns=3)")

        self.parameters.set(
                "battery",
                cache='active',
                mu='V',
                ordinal=10,
                first=timestamp,
                modules={"source":source},
                operator=f"source.retrive(serials={serial!r},times=times,columns=4)")

        self.parameters.set(
                "radar 1",
                cache='active',
                mu='mA',
                ordinal=5,
                first=timestamp,
                modules={"source":source},
                operator=f"source.retrive(serials={serial!r},times=times,columns=5)")

        self.parameters.set(
                "radar 2",
                cache='active',
                mu='mA',
                ordinal=6,
                first=timestamp,
                modules={"source":source},
                operator=f"source.retrive(serials={serial!r},times=times,columns=6)")
      
        self.parameters.set(
                "pluviometer",
                cache='active',
                mu='count',
                ordinal=7,
                first=timestamp,
                modules={"source":source},
                operator=f"source.retrive(serials={serial!r},times=times,columns=7)")

        if pluviometer is not None:
            self.parameters.set(
                'rain',
                cache='active',
                mu='mm/h',
                ordinal=4,
                first=timestamp,
                modules={"calc":"hielen3.tools.calc"}, 
                operands={"S0":self.parameters["pluviometer"].uuid},
                operator=f"calc.instant_velocity(calc.poly_trans2(S0,{pluviometer}))")

        if radar_1 is not None:
            self.parameters.set(
                'level 1',
                cache='active',
                mu="m.s.l.m.",
                ordinal=3,
                first=timestamp,
                modules={"calc":"hielen3.tools.calc"}, 
                operands={"S0":self.parameters["radar 1"].uuid},
                operator=f"{h_radar_1} - calc.poly_trans2(S0,{radar_1})")

            self.parameters.set(
                'free span 1',
                cache='active',
                mu="m",
                ordinal=1,
                first=timestamp,
                modules={"calc":"hielen3.tools.calc"}, 
                operands={"S0":self.parameters["radar 1"].uuid},
                operator=f"{h_min_span_1} - S0")


        if radar_2 is not None:
            self.parameters.set(
                'level 2',
                cache='active',
                mu="m.s.l.m.",
                ordinal=1,
                first=timestamp,
                modules={"calc":"hielen3.tools.calc"}, 
                operands={"S0":self.parameters["radar 2"].uuid},
                operator=f"{h_radar_2} - calc.poly_trans2(S0,{radar_2})")

            self.parameters.set(
                'free span 2',
                cache='active',
                mu="m",
                ordinal=2,
                first=timestamp,
                modules={"calc":"hielen3.tools.calc"}, 
                operands={"S0":self.parameters["radar 2"].uuid},
                operator=f"{h_min_span_2}-S0")



def retrive(serials=None,times=None, columns=None, folder='gestecno_rfi/data', func=None, **kwargs ):

    folder=Path(conf['incomepath']) / folder


    def __extract_gestecno__(path):
        a=DataFrame([],dtype='float64')
        try:
            a=read_csv(path,skiprows=2,parse_dates=True,header=None)
            if a.empty:
                a = read_csv(path,parse_dates=True,header=None)
                a = a[a[0].apply(lambda x: match('^\d{4}-\d{2}',x)).notna()]

            a.columns = [ 'times', *a.columns[1:] ]
        
        except Exception as e:
            pass

        return a


    if func is None:
        func = __extract_gestecno__

    if serials is None:
        serials = slice(None,None)

    if isinstance(serials,str):
          #serials=slice(serials,serials)
          serials=[serials]

    if isinstance(times,datetime):
        times=str(times)

    if times is None or isinstance(times,str):
        times=slice(times,None,None)
    
    start=times.start
    stop=times.stop

    if start is not None:
        datestart=str(datetime.fromisoformat(start).date())
    else:
        datestart=None

    times=slice(start,stop)

    dates=slice(datestart,stop)

    paths=Series(glob(f'{folder}/*/*/*/*'),dtype='object').apply(Path)

    sertime=DataFrame(
                paths.apply( lambda x: 
                    (
                        x.parts[-4], 
                        str(datetime(*map(int,x.parts[-3:])))
                        )
                    ).explode().values.reshape(paths.__len__(),2),
                columns=['serial','times']
            )
    sertime['path']=paths.apply(lambda x: str(x / "*"))
    sertime=sertime.set_index(['serial','times']).sort_index()

    df=DataFrame()

    try:
        sertime=sertime.to_frame()
    except Exception as e:
        pass

    if isinstance(serials, (list,set,tuple)):
        serials=list(sertime.index[
                sertime.index.isin(serials,level=0)
                ].droplevel(1).drop_duplicates()
                )
        if not serials.__len__():
            return df

    try:
        sertime=sertime.loc[(serials,dates), :]
    except KeyError as e:
        return df

    for serial,paths in sertime.groupby('serial'):
        u=concat(paths['path'].apply(glob).explode().apply(func).values)
        u['serial']=serial
        u=u.set_index(['serial','times'])
        df=concat([df,u])

    if columns is None:
        columns = list(df.columns)

    if not isinstance(columns,(list,tuple,set)):
        columns=[columns]

    columns = list(columns)

    df=df[columns].sort_index().loc[(serials, times), :]

    try:
        if serials.__len__() == 1:
            df = df.droplevel('serial',axis=0)
    except Exception as e:
        pass

    return df

