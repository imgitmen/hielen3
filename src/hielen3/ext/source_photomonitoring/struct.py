# coding: utf-8
import numpy as np
import pandas as pd
import re
import os
import PIL
import xarray as xr 
import datetime
import scipy.ndimage as snd
import matplotlib
import geojson
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from netCDF4 import Dataset, date2num
from json import JSONDecodeError
from numpy import datetime64, full
from pathlib import Path


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

    # ch (change detection) informations
    dataset.createVariable("ch","f4",("time","y","x",), fill_value=np.nan,zlib=True,least_significant_digit=3)
    dataset.variables["ch"].units="1"
    dataset.variables["ch"].long_name="change_detection"


    #zf=np.zeros((y_values.__len__(),x_values.__len__()))

    #feed_NC(dataset,timestamp,ns=zf,ew=zf,corr=zf)

    return dataset

def clean_feed_NC(target,time,**kwargs):

    origd = Dataset(target)

    newtarget=f"{origd.filepath()}.tmp"

    dataset = config_NC(newtarget,origd.timestamp,origd.variables['x'][:],origd.variables['y'][:])

    timevar = origd.variables['time']

    time=date2num( np.datetime64(time).tolist(), timevar.units)

    # If exists substitute
    position=np.where( timevar[:] == time )

    try:
        position=int(position[0])
    except TypeError as e:
        raise e
        
    dataset.variables['time'][:]=timevar[:position].data

    for k in [ 'corr', 'ns', 'ew', 'ch']:
        try:
            dataset.variables[k][:position,:,:]=origd.variables[k][:position,:,:].data
        except KeyError as e:
           pass 

    try:
        dataset.variables['time'][position:]=timevar[position+1:].data

        for k in [ 'corr', 'ns', 'ew', 'ch']:
            try:
                dataset.variables[k][position:,:,:]=origd.variables[k][position+1:,:,:].data
            except KeyError as e:
                pass 

    except Exception as e:
        print ("Ultimo")


    origd.close()
    dataset.close()

    Path(newtarget).replace(target)


   
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
    position=np.where( timevar[:] == time )

    try:
        position=int(position[0])
    except TypeError:
        position=timevar.shape[0]

    timevar[position]=time

    for k,w in kwargs.items():

        if w is None:
            w=full([
                    dataset.dimensions['y'].size,
                    dataset.dimensions['x'].size
                    ],fill_value=np.nan)

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
def _open_matrix(dataset, step_size=None, param=None, cmap=None, norm=None):

    '''
    params
    dataset: dataset at fixed time
    param:  "D"  displacment
            "NS" North-South"
            "EW" East-West
            "CC" Correlation Coefficient
            "CH" Change Detection
    '''
    # filtro con maschera di correlazione
    # se tutte le celle di corr sono null il minimo è TRUE altrimenti FALSE.
    # Inverto la condizione per sapere se c'è qualcosa

    try:
        span = norm.vmax - norm.vmin
    except Exception:
        span=1


    if step_size is None:
        step_size=1
    if param is None:
        param = "D"

    ns=dataset.ns
    ew=dataset.ew
    corr=dataset.corr
    ch=dataset.ch

    if param in ("D"):
        h=np.sqrt(ns**2+ew**2)

    if param in ("EW"): 
        h=ew
    
    if param in ("NS"):
        h=ns

    if param in ("CC"):
        h=corr

    if param in ("CH"):
        h=ch

    # upsampling

    h=snd.zoom(h,step_size,order=0,mode='nearest')

    Y=np.arange(0,h.shape[0])

    X=np.arange(0,h.shape[1])

    coords=[("y", Y), ("x", X)]


    heatmap=xr.DataArray(h, coords=coords)

    if param in ("NS","EW","CC","CH"):
        return dict(heatmap=heatmap,vectors=None)

    # Elaboro i versori 

    # upsampling
    a=snd.zoom(np.arctan2(ns,ew),step_size,order=0,mode='nearest')

    angle=xr.DataArray(a, coords=[("y", Y), ("x", X)])

    #riduco il versore
    rollingside=int(step_size*5)
    #CON MEDIA
    #https://stackoverflow.com/questions/52886703/xarray-multidimensional-binning-array-reduction-on-sample-dataset-of-4-x4-to

#    coeff=heatmap.rolling(x=rollingside).construct('tmp').isel(x=slice(1, None, rollingside)).mean('tmp',skipna=False)
#    coeff=heatmap.rolling(y=rollingside).construct('tmp').isel(y=slice(1, None, rollingside)).mean('tmp',skipna=False)
    
    """
    coeff=heatmap.rolling(x=rollingside).construct('tmp').isel(x=slice(1, None, rollingside)).mean('tmp',skipna=False)
    coeff=coeff.rolling(y=rollingside).construct('tmp').isel(y=slice(1, None, rollingside)).mean('tmp',skipna=False)
    

    angle=angle.rolling(x=rollingside).construct('tmp').isel(x=slice(1, None, rollingside)).mean('tmp',skipna=False)
    angle=angle.rolling(y=rollingside).construct('tmp').isel(y=slice(1, None, rollingside)).mean('tmp',skipna=False)
    """

    #SENZA MEDIA
    
    coeff=heatmap[::rollingside,::rollingside]
    angle=angle[::rollingside,::rollingside]
    

    # filtro **ARBITRARIAMENTE** quelli che superano il 2 sigma
    #coeff=coeff.where(coeff<coeff.mean()+coeff.std()*10)


    coeff=(coeff/span)

    #coeff=coeff.where(coeff>0)
    #coeff=coeff.where(coeff<50)
   
    # normalizzo su un valore adeguato
    # coeff=coeff/(coeff.mean())
    
    # applico il logaritmo per enfatizzare gli spostamenti minimi e
    # ridurre l'impatto visivo degli outlayers
    # coeff=np.log(1+coeff)
    
    # filtro l'angolo in base al grid del coefficiente
    #angle=angle.where(np.abs(coeff) > np.abs(coeff.mean()))

    X,Y= np.meshgrid(angle['x'],angle['y'])
    dY=np.sin(angle)*coeff
    dX=np.cos(angle)*coeff

    #if param in ("V"):
    #    heatmap=heatmap.where(heatmap is np.nan)
        
    return dict(heatmap=heatmap,vectors=(X,Y,dX,dY))


# CLASS METHOD
def _render(heatmap,vectors=None,cmap=None,norm=None, alphacolor=(0,0,0)):
    
    if cmap is None:
        cmap = LinearSegmentedColormap.from_list("mycmap", ["red","green","blue"])
    if norm is None:
        norm=Normalize(vmin=-2.5,vmax=2.5)

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


    ax.imshow(heatmap,alpha=0.65,origin='upper',cmap=cmap,norm=norm)
#    ax.imshow(heatmap,origin='upper',cmap=cmap,norm=norm)
    
    if vectors is not None:
        #ax.quiver(*vectors,width=0.0020,color='white',scale=100)
        ax.quiver(*vectors,color='white',units='dots',scale_units='xy',angles='uv',scale=0.01)

    fig.add_axes(ax)
    fig.canvas.draw()

    data = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (4,))[:, :, [1,2,3,0]]

    red, green, blue, alpha = data.T # Temporarily unpack the bands for readability

    sel = (alpha  == 0)

    data[..., :-1][sel.T] = alphacolor

    plt.close()

    return data


def generate_map(targetfile,timestamp=None, timeref=None, param=None,step_size=None,cmap=None,norm=None,threshold=0,**kwargs):

    dataset=xr.open_dataset(targetfile)

    if timestamp is None:
        timestamp = dataset.time[-1].values
    else:
        timestamp = datetime64(agoodtime(timestamp))

    ds1=dataset.sel(time=timestamp).squeeze()

    if param not in ["CH"]:
        m=ds1.corr.mean()
        if m is not np.nan and m:
            ds1=ds1.where(ds1.corr > threshold)

    try:
        timeref = datetime64(agoodtime(timeref)) 
    except Exception as e:
        timeref = None

    try:
        if np.isnat(timeref):
            timeref=None
    except Exception as e:
            timeref=None

    try:
        if np.isnat(timestamp):
            timestamp = None
    except Exception as e:
            timeref=None

    if timeref is not None:
        try:
            ds2=dataset.sel(time=timeref,method='nearest').squeeze()
            ds1=ds1-ds2
            ds1.attrs=dataset.attrs
        except Exception as e:
            pass

    try:
        ds1=ds1.sel(time=timestamp,method='nearest').squeeze()
    except Exception as e:
        pass

    managed=_open_matrix(dataset=ds1, param=param, step_size=step_size, cmap=cmap, norm=norm)

    dataset.close()

    return [timestamp, _render(**managed, cmap=cmap, norm=norm )]



def extract_data(targetfile,geometry=None,times=None,output="D",timeref=None, geographic=False, **kwargs):

    '''
    params 
    geom: point to extract
    timefrom: time lower limit
    timeto: time upper limit
    output: "D" Displacement
           "NS" North-South component
           "EW" Eeast-West component
           "CC" Correlation Coefficient
           "CH" Change Detection
    '''
    
    dataset=xr.open_dataset(targetfile)

    #1 manipola json
    #2 se json è un punto extrac "nearest"
    #3 altrimenti boundigbox e slices


    if times is None:
        times = slice(None,None,None)

    if geometry is None:
        return None

    """
        geometry = geojson.Point([800,800])
    else:
        geometry = geojson.loads(geojson.dumps(geometry))

    coords=list(geojson.utils.coords(geometry[0]))
    """


    try:
        #TODO ricorda dataframe.rio.clip(geometries)
        #print (geometry)
        coords=list(geojson.utils.coords(geometry[0]))

        if not geographic:
            coords = list( map( lambda l: [l[0], dataset.y[-1]-l[1]], coords ) )


        geotype=str(geometry[0]['type'])
        name=""

        #if isinstance(geometry[0],geojson.Point) :
        if geotype == 'Point':
            query={
                    'method':'nearest', 
                    **dict(zip(['x','y'],coords[0]))
                    }
            #name="_".join(map(str,coords[0]))
            name='nearest'

        #elif isinstance(geometry[0],geojson.Polygon):
        elif geotype == 'Polygon':
            coords=pd.DataFrame(coords)

            dirx= dataset.x[0] < dataset.x[-1] and 1 or -1
            diry= dataset.y[0] < dataset.y[-1] and 1 or -1

            query={
                    'method':None, 
                    "x":slice(coords[0].min(),coords[0].max(),dirx), 
                    "y":slice(coords[1].min(),coords[1].max(),diry)
                    }
            name='mean'

        else:
            raise ValueError("Unmanaged geometry Type")
        
        
    except Exception as e:
        return None


    #print (query)

    """
    def isbasetime(self,time):
        try:
            return np.datetime64(time) == np.datetime64(self.reftime)
        except Exception:
            return False
    """

    timeref=agoodtime(timeref)

    dst=dataset.sel(**query).sel(time=times)

#    if timeref is not None and not targetfile.isbasetime(timeref):
    if timeref is not None:
        try:
            ref=dataset.sel(time=timeref,**query).squeeze()
            dst['ns']=dst.ns-ref.ns
            dst['ew']=dst.ew-ref.ew
            dst=dst.sel(time=slice(timeref,None,None))

        except Exception as e:
            pass

    if output in ("D"):
        out=np.sqrt(dst.ns**2+dst.ew**2)

    #if output in ("V"):
    #    out=np.rad2deg(np.arctan2(dst.ns,dst.ew))

    if output in ("NS"):
        out=dst.ns

    if output in ("EW"):
        out=dst.ew

    if output in ("CC"):
        out=dst.corr

    if output in ("CH"):
        out=dst.ch

    if name=='mean':
        try:
            out=out.mean(dim='x',skipna=True).mean(dim='y',skipna=True)
        except Exception as e:
            pass

    out.name=name
    out=out.to_dataframe().reset_index().set_index('time')
    out=out.apply(lambda a: { "name":name, "value":a[name] }, axis=1, result_type='expand')
    out=out.reset_index().set_index(['time','name']).unstack().droplevel(0,axis=1)
 
    out = out[out.columns[0]]#.map('{:,.4f}'.format)

    dataset.close()

    return out


