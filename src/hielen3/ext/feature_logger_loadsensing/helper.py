# coding=utf-8

from hielen3.ext.feature_datetree_filesystem_source import loggers, retriver
from pandas import read_csv, DataFrame, Series, concat

folders=[
        {
            'type':'loadsensing',
            'path':'loadsensing/data'
            },
        ]

func_loggers=loggers( folders )

vc= [
        'Duration-Seconds',
        'Particle-PeakVelocity-Axis-X-Event-mm/s',
        'Predominant-Frequency-Axis-X-Event-Hz',
        'Particle-PeakVelocity-Axis-Y-Event-mm/s',
        'Predominant-Frequency-Axis-Y-Event-Hz',
        'Particle-PeakVelocity-Axis-Z-Event-mm/s',
        'Predominant-Frequency-Axis-Z-Event-Hz',
        'Composed-Vector-PPV-mm/s',
        'Temperature-Celsius'
    ]

cvc=[
        'Duration',
        'Particle-PeakVelocity-Axis-X',
        'Predominant-Frequency-Axis-X',
        'Particle-PeakVelocity-Axis-Y',
        'Predominant-Frequency-Axis-Y',
        'Particle-PeakVelocity-Axis-Z',
        'Predominant-Frequency-Axis-Z',
        'Composed-Vector-PPV',
        'Temperature'
    ]


@retriver(func_loggers)
def retrive(path):

    a=DataFrame([],dtype='float64')

    try:
        a=read_csv(path,skiprows=9,parse_dates=[0])

        if "Date-and-time" in a.columns and "Timestamp-Event" in a.columns:
            d=a["Date-and-time"].dropna().copy()
            d1=a["Timestamp-Event"].astype("datetime64[ns]").dropna().copy()
            d1.name='Date-and-time'             
            a=a.drop(["Date-and-time","Timestamp-Event"],axis=1).copy()
            a["Date-and-time"]=concat([d,d1])

        a.columns=[ a.replace("Timestamp-Event","Date-and-time") for a in a.columns ]
        
        isvib=Series(a.columns).apply(lambda x: "Composed-Vector-PPV" in x).any()

        if isvib:
            a=a.set_index("Date-and-time")
            a.columns=[ "-".join(c.split("-")[1:]) for c in a.columns ]
            a=a[vc]
            a.columns=[ c.split("-Event")[0] for c in a.columns ]
            a.columns=[ c.split("-mm/s")[0] for c in a.columns ]
            a.columns=[ c.split("-Seconds")[0] for c in a.columns ]
            a.columns=[ c.split("-Celsius")[0] for c in a.columns ]
            a=a[a["Composed-Vector-PPV"].notna()]
            a.index.name="times"
            a=a.reset_index()
            a=a[["times",*cvc]]
        else:

            ## ALCUNI HANNO QUESTA COLONNA ALTRI NO :-(
            col_to_test="InternalTempInCelsius"

            has_col_to_test=Series(a.columns).apply(lambda x: col_to_test in x).any()

            if not has_col_to_test:
                a[col_to_test]=None
                a=a[[a.columns[0],col_to_test,*a.columns[1:-1]]]

            a.columns=[ 'times',*list(range(1,a.columns.__len__()))]
        #a.columns = [ 'times', *a.columns[1:] ]

    except Exception as e:
        print("WARN : ", path)
        a=DataFrame([],dtype='float64')
        #raise e #DEBUG
        pass

    return a

