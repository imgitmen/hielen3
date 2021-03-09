# coding: utf-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import xarray as xr, datetime
import scipy.ndimage as snd
import re
from netCDF4 import Dataset, date2num
import os
import PIL


def config_NC(target, timestamp, x_values, y_values):

    """
    Crea il file netCDF secondo un formato standard

    returns: la struttura dati del file NetCDF

    params
    tagetfile: nome del file
    refitime: tempo zero
    y_values: array delle y
    x_values: array  delle x

    """

    dataset = Dataset(target, 'w', format="NETCDF4")
    dataset.Conventions="CF-1.7"
    dataset.timestamp= agoodtime(timestamp)

    # time informations
    dataset.createDimension("time", None)
    dataset.createVariable("time","f8",("time",))
    dataset.variables["time"].units=f"hours since {timestamp}"
    dataset.variables["time"].calendar="standard"
    dataset.variables["time"].long_name="observation_time"

    # y informations
    dataset.createDimension("y", y_values.__len__())
    dataset.createVariable("y","f4",("y",))
    dataset.variables["y"].units="1"
    dataset.variables["y"].long_name="projection_y_coordinate"
    dataset.variables["y"][:]=y_values

    # x informations
    dataset.createDimension("x", x_values.__len__())
    dataset.createVariable("x","f4",("x",))
    dataset.variables["x"].units="1"
    dataset.variables["x"].long_name="projection_x_coordinate"
    dataset.variables["x"][:]=x_values

    # corr (correlation coefficient) informations
    dataset.createVariable("corr","f4",("time","y","x",), fill_value=1,zlib=True,least_significant_digit=3)
    dataset.variables["corr"].units="1"
    dataset.variables["corr"].long_name="correlation_coefficient"


    # ns (north-south) informations
    dataset.createVariable("ns","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=3)
    dataset.variables["ns"].units="px"
    dataset.variables["ns"].long_name="north_south_axis_displacement"

    # ew (east-west) informations
    dataset.createVariable("ew","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=3)
    dataset.variables["ew"].units="px"
    dataset.variables["ew"].long_name="east_west_axis_displacement"


    #zf=np.zeros((y_values.__len__(),x_values.__len__()))

    #feed_NC(dataset,timestamp,ns=zf,ew=zf,corr=zf)

    return dataset

   
def feed_NC(target,time,**kwargs):

    """
    Appende i grid al file netCDF
    
    target: netCDF4.Dataset or path to a valid .nc file
    time: timestamp del dato
    kwarg: dict nomevariabile:datagrid

    """

    if isinstance(target, Dataset):
        dataset = target
    else:
        dataset = Dataset(target, 'a', format="NETCDF4")
        
    timevar = dataset.variables['time']

    time=date2num( np.datetime64(time).tolist(), timevar.units)
    
    # If exists substitute
    position=np.where( timevar == time )

    try:
        position=int(position[0])
    except TypeError:
        position=timevar.shape[0]

    timevar[position]=time

    for k,w in kwargs.items():
        if w is not None:
            y_slice=slice(0,w.shape[0])
            x_slice=slice(0,w.shape[1])
            try:
                dataset.variables[k][position,y_slice,x_slice] = w
            except KeyError as e:
                raise(e)
                pass

    return dataset



def agoodtime(t):
    try:
        t=np.datetime64(t)
        assert not np.isnat(t)
        t=str(t)
    except Exception:
        t=None

    return t


#CASS METHOD
def _open_matrix(dataset, step_size=1, param="RV"):

    '''
    params
    dataset: dataset at fixed time
    param: "RV" result + vector
            "R"  results
            "V"  vector
            "NS" North-South"
            "EW" East-West
    '''
    # filtro con maschera di correlazione
    # se tutte le celle di corr sono null il minimo è TRUE altrimenti FALSE.
    # Inverto la condizione per sapere se c'è qualcosa

    ns=dataset.ns
    ew=dataset.ew

    if param in ("RV","R","V"):
        h=np.sqrt(ns**2+ew**2)

    if param in ("EW"): 
        h=ew
    
    if param in ("NS"):
        h=ns

    # upsampling
    h=snd.zoom(h,step_size,order=0,mode='nearest')

    Y=np.arange(0,h.shape[0])

    X=np.arange(0,h.shape[1])


    heatmap=xr.DataArray(h, coords=[("y", Y), ("x", X)])

    if param in ("R","NS","EW"):
        return dict(heatmap=heatmap,vectors=None)

    # A questo punto solo RV o V
    # Elaboro i versori 

    # upsampling
    a=snd.zoom(np.arctan2(ns,ew),step_size,order=0,mode='nearest')

    angle=xr.DataArray(a, coords=[("y", Y), ("x", X)])

    #riduco il versore
    rollingside=int(step_size*6)
    #CON MEDIA
    #https://stackoverflow.com/questions/52886703/xarray-multidimensional-binning-array-reduction-on-sample-dataset-of-4-x4-to

    coeff=heatmap.rolling(x=rollingside).construct('tmp').isel(x=slice(1, None, rollingside)).mean('tmp',skipna=False)
    coeff=heatmap.rolling(y=rollingside).construct('tmp').isel(y=slice(1, None, rollingside)).mean('tmp',skipna=False)

    angle=angle.rolling(x=rollingside).construct('tmp').isel(x=slice(1, None, rollingside)).mean('tmp',skipna=False)
    angle=angle.rolling(y=rollingside).construct('tmp').isel(y=slice(1, None, rollingside)).mean('tmp',skipna=False)
    #SENZA MEDIA
    '''
    coeff=coeff[::rollingside,::rollingside]
    '''

    # filtro **ARBITRARIAMENTE** quelli che superano il 2 sigma
    # coeff=coeff.where(coeff<coeff.mean()+coeff.std()*2)
   
    # normalizzo su un valore adeguato
    coeff=coeff/(coeff.mean()*4)
    
    # applico il logaritmo per enfatizzare gli spostamenti minimi e
    # ridurre l'impatto visivo degli outlayers
    # coeff=np.log(1+coeff)
    
    # filtro l'angolo in base al grid del coefficiente
    angle=angle.where(np.abs(coeff) > np.abs(coeff.mean()))

    X,Y= np.meshgrid(angle['x'],angle['y'])
    dY=np.sin(angle)*coeff
    dX=np.cos(angle)*coeff

    if param in ("V"):
        heatmap=heatmap.where(heatmap is np.nan)
        
    return dict(heatmap=heatmap,vectors=(X,Y,dX,dY))


# CLASS METHOD
def _render(heatmap,vectors=None,colors=["green","red","blue"],vmin=0,vmax=5):
    
    cmap = LinearSegmentedColormap.from_list("mycmap", colors)

    W=heatmap.shape[1]
    H=heatmap.shape[0]

    plt.tight_layout=dict(pad=0)
    fig = plt.figure()
    fig.tight_layout=dict(pad=0)
    fig.frameon=False
    fig.dpi=72
    fig.set_size_inches(W/fig.dpi,H/fig.dpi)
    fig.facecolor="None"
    fig.linewidth=0

    ax=plt.Axes(fig,[0,0,1,1])
    ax.set_axis_off()

    ax.imshow(heatmap,alpha=0.20,origin='upper',cmap=cmap,norm=None,vmin=vmin,vmax=vmax)
    
    if vectors is not None:
        ax.quiver(*vectors,width=0.0008,color='white',scale=100)

    fig.add_axes(ax)
    fig.canvas.draw()

    data = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (4,))[:, :, [3,2,1,0]]

    return data


def generate_map(targetfile,timestamp=None, timeref=None, param=None,step_size=None,colors=None,vmin=None,vmax=None):


    if timestamp is None:
        pass
    if param is None:
        param="R"
    if step_size is None:
        stap_size=1
    if colors is None:
        colors=["red","green","blue"]
    if vmin is None:
        vmin=-150
    if vmax is None:
        vmax= 150


    dataset=xr.open_dataset(targetfile)


    if timestamp is None:
        timestamp = str(dataset.time[-1].values)
    else:
        timestamp = agoodtime(timestamp)

    ds1=dataset.sel(time=timestamp)
    ds1=ds1.where(ds1.corr > 0)

    if timeref is not None:
        timeref = agoodtime(timeref)
        ds2=dataset.sel(time=timeref)
        ds2=ds2.where(ds2.corr > 0)
        ds1=ds1-ds2
        ds1.attrs=dataset.attrs
        
    managed=_open_matrix(dataset=ds1, param=param, step_size=step_size)

    return _render(**managed, colors=colors, vmin=vmin, vmax=vmax )


class Render():

    @property
    def timeline(self):
        times = self.dataset.time.values
        return list(map(lambda x:str(x).replace('.000000000',''),(times)))

    @property
    def reftime(self):
        return self.dataset.timestamp

    def isbasetime(self,time):
        try:
            return np.datetime64(time) == np.datetime64(self.reftime)
        except Exception:
            return False




    def extract_data(self,geom=(0,0),timefrom=None,timeto=None,param="R",timeref=None):

        '''
        params
        geom: point to extract
        timefrom: time lower limit
        timeto: time upper limit
        param: "R" result (the module itself)
                "NS" North-South component
                "EW" Eeast-West component
        '''

        timefrom=agoodtime(timefrom)
        timeto=agoodtime(timeto)
        timeref=agoodtime(timeref)

        dst=self.dataset.sel(x=geom[0],y=geom[1],method='nearest').sel(time=slice(timefrom,timeto))

        if timeref is not None and not self.isbasetime(timeref):
            ref=self.dataset.sel(x=geom[0],y=geom[1],time=timeref,method='nearest')
            dst['ns']=dst.ns-ref.ns
            dst['ew']=dst.ew-ref.ew
        
        if param in ("R", "RV"):
            out=np.sqrt(dst.ns**2+dst.ew**2)

        if param in ("V"):
            out=np.rad2deg(np.arctan2(dst.ns,dst.ew))

        if param in ("NS"):
            out=dst.ns

        if param in ("EW"):
            out=dst.ew

        out = pd.DataFrame(out,index=out.time.values,columns=['xxx']).dropna()

        return out

     
