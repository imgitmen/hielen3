# coding: utf-8
import numpy as np
import pandas as pd
import re
from netCDF4 import Dataset, date2num
import os

    timestamp = fields.Str(required=True, allow_none=False)
    master_image = fileds.Str(required=True, allow_none=False)
    step_size = fields.Str(required=False, default="8")
    window_size_change = fields.Str(required=False,default="0")
    world_file = fields.Str(required=False,default=None)
    crs: "EPSG:3857"



class NCMangler():

    def __init__(self, targetfile=None,dims=None,timestamp=None,step_size=8,window_size_change=0,**kwargs):
        """
        Crea il file netCDF secondo un formato standard

        returns: la struttura dati del file NetCDF

        params
        name: nome del file
        y_values: dimensione delle y
        x_values: dimensione delle x
        refitime: tempo zero

        """

        if not os.path.exists(targetfile):


            xdim=(dims[1]-window_size_change*2)/step_size
            ydim=(dims[2]-window_size_change*2)/step_size

            y_values=np.arange(window_size_change,xdim)*step_size
            x_values=np.arange(window_size_change,ydim)*step_size

            rootgrp = Dataset(targetfile, 'w', format="NETCDF4")
            rootgrp.Conventions="CF-1.7"

            rootgrp.timestamp= str(np.datetime64(timestamp))

            # time informations
            rootgrp.createDimension("time", None)
            rootgrp.createVariable("time","f8",("time",))
            rootgrp.variables["time"].units=f"hours since {timestamp}"
            rootgrp.variables["time"].calendar="standard"
            rootgrp.variables["time"].long_name="observation_time"
            
            # y informations
            rootgrp.createDimension("y", y_values.__len__())
            rootgrp.createVariable("y","f4",("y",))
            rootgrp.variables["y"].units="1"
            rootgrp.variables["y"].long_name="projection_y_coordinate"
            rootgrp.variables["y"][:]=y_values
            
            # x informations
            rootgrp.createDimension("x", x_values.__len__())
            rootgrp.createVariable("x","f4",("x",))
            rootgrp.variables["x"].units="1"
            rootgrp.variables["x"].long_name="projection_x_coordinate"
            rootgrp.variables["x"][:]=x_values

            '''
            # module information
            rootgrp.createVariable("module","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=3)
            rootgrp.variables["module"].units="1"
            rootgrp.variables["module"].long_name="module_of_relativie_displacement"

            # angle informations
            rootgrp.createVariable("angle","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=2)
            rootgrp.variables["angle"].units="radians"
            rootgrp.variables["angle"].long_name="versor_of_relative_displacement"
            '''

            
            # ns (north-south) informations
            rootgrp.createVariable("ns","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=3)
            rootgrp.variables["ns"].units="px"
            rootgrp.variables["ns"].long_name="north_south_axis_displacement"

            # ew (east-west) informations
            rootgrp.createVariable("ew","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=3)
            rootgrp.variables["ew"].units="px"
            rootgrp.variables["ew"].long_name="east_west_axis_displacement"
            

            # corr (correlation coefficient) informations
            rootgrp.createVariable("corr","f4",("time","y","x",),fill_value=np.nan,zlib=True,least_significant_digit=3)
            rootgrp.variables["corr"].units="1"
            rootgrp.variables["corr"].long_name="correlation_coefficient"

            rootgrp.close()
        
        self.dataset= Dataset(targetfile, 'a', format="NETCDF4")
        
    
    # CLASS METHOD
    def _prepare_frames(fileNS=None,fileEW=None,fileCORR=None):

        NS = pd.read_csv(fileNS,header=None)
        EW = pd.read_csv(fileEW,header=None)
        CORR = pd.read_csv(fileCORR,header=None)
        #MO = np.sqrt(NS**2 + EW**2)
        #AN = np.arctan2(NS,EW)

        return {"ns":NS,"ew":EW,"corr":CORR}
        #return {"module":MO,"angle":AN, "corr":CORR}


    def _append_data(self,time,**kwargs):

        """
        Appende i grid al file netCDF

        rootgrp: Struttura NetCDF
        time: timestamp del dato
        var: variablile da riempire
        value: grid da appendere

        """
        
        dataset=self.dataset
        time=date2num(time,dataset.variables['time'].units)

        position=np.where(dataset.variables['time'] == time )

        try:
            position=int(position[0])
        except TypeError:
            position=dataset.variables['time'].shape[0]

        dataset.variables['time'][position]=time

        for var,val in kwargs.items():
            val.index=dataset['y'][:].data
            val.columns=dataset['x'][:].data
            dataset.variables[var][position,:,:] = val

        return dataset


    def coalesce_files(self,time=None,fileNS=None,fileEW=None,fileCORR=None):
        frames=NCMangler._prepare_frames(fileNS=fileNS,fileEW=fileEW,fileCORR=fileCORR)
        self._append_data(time,**frames)
        return self

    def close(self):
        self.dataset.close()

def agoodtime(t):

    try:
        t=np.datetime64(t)
        assert not np.isnat(t)
        t=str(t)
    except Exception:
        t=None
    return t

