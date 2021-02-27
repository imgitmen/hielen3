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


def config_NC(target, timestamp, x_values, y_values, step_size=None, x_offset=None, y_offset=None):

    """
    Crea il file netCDF secondo un formato standard

    returns: la struttura dati del file NetCDF

    params
    tagetfile: nome del file
    refitime: tempo zero
    y_values: array delle y
    x_values: array  delle x

    """

    try:
        step_size=int(step_size)
    except Exception as e:
        step_size=1

    try:
        x_offset=int(step_size)
    except Exception as e:
        x_offset=0

    try:
        y_offset=int(step_size)
    except Exception as e:
        y_offset=0


    y_values=y_values[y_offset::step_size]
    x_values=x_values[x_offset::step_size]

    dataset = Dataset(target, 'w', format="NETCDF4")
    dataset.Conventions="CF-1.7"
    dataset.timestamp= agoodtime(timestamp)
    dataset.step_size = step_size

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
    dataset.variables["y"].pixel_offset=y_offset
    dataset.variables["y"][:]=y_values

    # x informations
    dataset.createDimension("x", x_values.__len__())
    dataset.createVariable("x","f4",("x",))
    dataset.variables["x"].units="1"
    dataset.variables["x"].long_name="projection_x_coordinate"
    dataset.variables["x"].pixel_offset=x_offset
    dataset.variables["x"][:]=x_values

    # ns (north-south) informations
    dataset.createVariable("ns","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=3)
    dataset.variables["ns"].units="px"
    dataset.variables["ns"].long_name="north_south_axis_displacement"

    # ew (east-west) informations
    dataset.createVariable("ew","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=3)
    dataset.variables["ew"].units="px"
    dataset.variables["ew"].long_name="east_west_axis_displacement"


    # corr (correlation coefficient) informations
    dataset.createVariable("corr","f4",("time","y","x",),fill_value=np.nan,zlib=True,least_significant_digit=3)
    dataset.variables["corr"].units="1"
    dataset.variables["corr"].long_name="correlation_coefficient"

    zf=np.zeros((y_values.__len__(),x_values.__len__()))

    feed_NC(dataset,timestamp,ns=zf,ew=zf,corr=zf)

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
def _open_matrix(dataset, output="RV", correlation=0):

    '''
    params
    dataset: dataset at fixed time
    output: "RV" result + vector
            "R"  results
            "V"  vector
            "NS" North-South"
            "EW" East-West
    '''
    # filtro con maschera di correlazione
    # se tutte le celle di corr sono null il minimo è TRUE altrimenti FALSE.
    # Inverto la condizione per sapere se c'è qualcosa
    if correlation and not ns.corr.isnull().min():
        ns=dataset.ns.where(dataset.corr >= correlation)
        ew=dataset.ew.where(dataset.corr >= correlation)
    else:
        ns=dataset.ns
        ew=dataset.ew

    step_size = dataset.step_size
    
    if output in ("RV","R","V"):
        h=np.sqrt(ns**2+ew**2)

    if output in ("EW"): 
        h=ew
    
    if output in ("NS"):
        h=ns

    # upsampling
    h=snd.zoom(h,step_size,order=0,mode='nearest')

    Y=np.arange(0,h.shape[0])
    X=np.arange(0,h.shape[1])

    heatmap=xr.DataArray(h, coords=[("y", Y), ("x", X)])

    if output in ("R","NS","EW"):
        return dict(heatmap=heatmap,vectors=None,dims=h.shape)

    # A questo punto solo RV o V
    # Elaboro i versori 

    # upsampling
    a=snd.zoom(np.arctan2(ns,ew),step_size,order=0,mode='nearest')

    angle=xr.DataArray(a, coords=[("y", Y), ("x", X)])

    #riduco il versore
    rollingside=100
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
    coeff=coeff/coeff.mean()
    
    # applico il logaritmo per enfatizzare gli spostamenti minimi e
    # ridurre l'impatto visivo degli outlayers
    # coeff=np.log(1+coeff)
    
    # filtro l'angolo in base al grid del coefficiente
    angle=angle.where(coeff)

    X,Y= np.meshgrid(angle['x'],angle['y'])
    dY=np.sin(angle)*coeff
    dX=np.cos(angle)*coeff

    if output in ("V"):
        heatmap=heatmap.where(heatmap is np.nan)
        
    return dict(heatmap=heatmap,vectors=(X,Y,dX,dY),dims=h.shape)


# CLASS METHOD
def _render(heatmap,vectors=None,colors=["green","red","blue"],vmin=0,vmax=5):
    
    cmap = LinearSegmentedColormap.from_list("mycmap", colors)

    W=heatmap.shape[1]
    H=heatmap.shape[1]

    plt.tight_layout=dict(pad=0)
    fig = plt.figure()
    fig.tight_layout=dict(pad=0)
    fig.frameon=False
    fig.dpi=72
    fig.set_size_inches(W/dpi,H/dpi)
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


def generate_map(targetfile,timestamp=None, timeref=None, output="RV",cmap=["green","red","blue"],vmin=-2.5,vmax=2-5):

    dataset=xr.open_dataset(targetfile)

    if timestamp is None:
        timestamp = str(dataset.time[-1].values)
    else:
        timestamp = agoodtime(timestamp)


    if timeref is None:
        timeref = str(dataset.time[0].values)
        correlation=0.01
    else:
        timeref = agoodtime(timeref)
        correlation = 0



    print ("a")
    #Nel caso di ref zero il risultato è dato dal dataset in "timestamp"

    d1=dataset.sel(time=timestamp).compute()

    d2=dataset.sel(time=timeref).compute()

    d3=(d1-d2).compute()

    print (d2)
    managed=_open_matrix(dataset=dataset, output=output, correlation=correlation )



    print ("c")
    imgarray = _render(**managed, colors=colors, vmin=vmin, vmax=vmax )

    print ("")
#    void=xr.DataArray(h, coords=[("y", Y), ("x", X)])


#    result = PIL.Image.fromarray(imgarray)
#    img = PIL.Image.new(result.mode, (width, height), (0,0,0,0))
#    img.paste(result, dataset.x.pixels_offset,dataset.y.pixels_offset)
                
#    filename=f"{re.sub('[^\d]','',timeref)}_{re.sub('[^\d]','',timestamp)}.tiff"




class Render():

    def __init__(self,targetfile='./incomes/sag.nc', gridratio=8, **kwargs):
        self.gridratio=gridratio



   
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




    def extract_data(self,geom=(0,0),timefrom=None,timeto=None,output="R",timeref=None):

        '''
        params
        geom: point to extract
        timefrom: time lower limit
        timeto: time upper limit
        output: "R" result (the module itself)
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
        
        if output in ("R", "RV"):
            out=np.sqrt(dst.ns**2+dst.ew**2)

        if output in ("V"):
            out=np.rad2deg(np.arctan2(dst.ns,dst.ew))

        if output in ("NS"):
            out=dst.ns

        if output in ("EW"):
            out=dst.ew

        out = pd.DataFrame(out,index=out.time.values,columns=['xxx']).dropna()

        return out

     
