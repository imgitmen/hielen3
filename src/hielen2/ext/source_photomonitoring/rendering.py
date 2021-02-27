# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr, datetime
import scipy.ndimage as snd
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

def agoodtime(t):
    try:
        t=np.datetime64(t)
        assert not np.isnat(t)
        t=str(t)
    except Exception:
        t=None

    return t



class Render():

    def __init__(self,targetfile='./incomes/sag.nc', gridratio=8, **kwargs):
        self.dataset=xr.open_dataset(targetfile)
        self.gridratio=gridratio

    #CASS METHOD
    def _open_matrix(ns=None, ew=None, corr=None, output="RV", gridratio=8):

        '''
        params
        dataset: dataset at fixed time
        output: "RV" result + vector
                "R"  results
                "V"  vector
                "NS" North-South"
                "EW" East-West
        '''
        # filtro con maschera di coerenza e faccio zoom
        
        if corr is not None:
            ns=ns.where(corr >= 0)
            ew=ew.where(corr >= 0)

        if output in ("RV","R","V"):
            h=np.sqrt(ns**2+ew**2)

        if output in ("EW"): 
            h=ew
        
        if output in ("NS"):
            h=ns

        # upsampling
        h=snd.zoom(h,gridratio,order=0,mode='nearest')

        Y=np.arange(0,h.shape[0])
        X=np.arange(0,h.shape[1])

        heatmap=xr.DataArray(h, coords=[("y", Y), ("x", X)])

        if output in ("R","NS","EW"):
            return dict(heatmap=heatmap,vectors=None,dims=h.shape)

        # A questo punto solo RV o V
        # Elaboro i versori 

        # upsampling
        a=snd.zoom(np.arctan2(ns,ew),gridratio,order=0,mode='nearest')

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
    def _print_image(heatmap=None,vectors=None,colors=["green","red","blue"],vmin=0,vmax=5,dims=None):
        
        cmap = LinearSegmentedColormap.from_list("mycmap", colors)

        W=dims[1]#+64
        H=dims[0]#+64

        dpi=72

        plt.tight_layout=dict(pad=0)
        fig = plt.figure()
        fig.tight_layout=dict(pad=0)
        fig.frameon=False
        fig.dpi=dpi
        fig.set_size_inches(W/dpi,H/dpi)
        fig.facecolor="None"
        fig.linewidth=0
        ax=plt.Axes(fig,[0,0,1,1])
        ax.set_axis_off()

        if heatmap is not None:
            ax.imshow(heatmap,alpha=0.20,origin='upper',cmap=cmap,norm=None,vmin=vmin,vmax=vmax)
        
        if vectors is not None:
            ax.quiver(*vectors,width=0.0008,color='white',scale=100)

        fig.add_axes(ax)
        fig.canvas.draw()

        data = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)

        data = data.reshape(fig.canvas.get_width_height()[::-1] + (4,))[:, :, [3,2,1,0]]

        return data

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


    def generate_map(self,timestamp=None, timeref=None, output="RV"):

        timestamp = agoodtime(timestamp)
        timeref= agoodtime(timeref)

        if timestamp is None:
            timestamp = str(self.dataset.time[-1].values)

        dataset=self.dataset.sel(time=timestamp)
        corr=dataset.corr


        if timeref is not None and not self.isbasetime(timeref):
            dataref=self.dataset.sel(time=timeref)
            dataset = dataset-dataref
            corr = None

        colors=["green","red","blue"]
        vmin=0
        vmax=5

        if output in ("NS","EW"):
            colors=["blue","green","red"]
            vmin=-2.5
            vmax=2.5


        managed=Render._open_matrix(
                ns=dataset.ns,
                ew=dataset.ew,
                corr=corr,
                output=output,
                gridratio=self.gridratio
                )

        return Render._print_image(
                **managed,
                colors=colors,
                vmin=vmin,
                vmax=vmax
                )
                


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

     
