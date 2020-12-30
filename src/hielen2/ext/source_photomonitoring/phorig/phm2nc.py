#!/usr/bin/python
# coding: utf-8
import ftputil
import re
import glob
import datetime
import os
import pandas as pd
import xarray as xr
import datamaps

class Crawler():

    class Backlistener():

        def __init__(self, total, verbose=0):
            self.verbose = verbose
            self.total = total
            self.sum = 0

        def callback(self,chunk):
            if self.verbose > 0:
                self.sum=self.sum+chunk.__len__()

        def done(self):
            return self.sum-self.total == 0


    def __init__( self, host=None, user=None, passwd=None, reftime=None, searchpath=".", cacheftp=".", targetfile=None, verbose=0, **kwargs ):
        self.searchpath = searchpath
        self.cacheftp = cacheftp
        self.verbose=verbose
        self.reftime=reftime
        self.targetfile=targetfile
        self.ftp=None
        if host is not None:
            self.ftp=ftputil.FTPHost(host,user,passwd)
        self.appenduri=self.calculate_raw_index_delta()
        self.new_dates=self.appenduri.index.drop_duplicates().sort_values()

    def list (self):
        li = []
        if self.ftp is not None:
            li = self.ftp.listdir(self.searchpath)
        else:
            li = glob.glob(os.path.join(self.searchpath,'*'))

        #return list(map(lambda x: re.sub(f'{self.searchpath}/','',x), li ))
        return list(map(lambda x: x.split('/')[-1], li ))


    def open(self, filename):

        sourcefilepath=filepath=os.path.join(self.searchpath,filename)

        if self.ftp is not None:
            cachesearchpath=os.path.join(self.cacheftp,self.searchpath)
            if not os.path.isdir(cachesearchpath):
                os.makedirs(cachesearchpath)
            filepath=os.path.join(cachesearchpath,filename)
            if not os.path.isfile(filepath):
                try:
                    if self.verbose > 0:
                        print ("Downloading",filename)
                    bl=Crawler.Backlistener(self.ftp.lstat(sourcefilepath)[6],self.verbose)
                    self.ftp.download(sourcefilepath,filepath,bl.callback)
                    assert bl.done() == True
                except Exception:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    filepath=None
        
        return filepath

    def fix(self,filename):
        if self.ftp is not None:
            cachefilepath=os.path.join(self.cacheftp,self.searchpath,filename)
            sourcefilepath=os.path.join(self.searchpath,filename)
            if os.path.exists(cachefilepath):
                rtotal = self.ftp.lstat(sourcefilepath)[6]
                ltotal = os.lstat(cachefilepath)[6]
                if rtotal != ltotal:
                    os.remove(cachefilepath)


    def calculate_raw_index_delta(self):

        li = self.list()


        # filtro solo i csv eliminando le resultanti (calcolate in seguito) e le elaborazioni alternative (multistack<a|b|..|z>)
        #li= [ a for a in li if ( re.search("\.csv",a) and not re.search("_RES_",a))] # and re.search("multistack[0-9]+_",a))]


        li= [ a for a in li if ( re.search("\.csv",a) and not re.search("_RES_",a) and re.search("displacement|correlation",a) ) ] # and re.search("multistack[0-9]+_",a))]

        # separo i campi
        li=[[re.split(' ',re.sub('[^\d]+',' ',n)),n] for n in li]

        # creo un array bidimensionale in cui per ogni riga trovo:
        #   a) il tipo ('EW','NS','CORR')
        #   b) il datetime dell'imagine Master
        #   c) il datetime dell'imagine Slave
        #   d) l'intero filename
        li = [ 
            [
                (re.search('EW',ds[1]) and "EW") or (re.search('NS',ds[1]) and "NS" ) or ( re.search('corr',ds[1]) and "CORR"),
                datetime.datetime(*map(int,ds[0][9:15])),
                datetime.datetime(*map(int,ds[0][2:8])),
                ds[1]
            ] for ds in li
        ]

        li = pd.DataFrame(li,columns=['tipo','time_ref','time','file']).set_index(['time']).sort_index() 

        print (li)

        if self.reftime is not None: li = li[li['time_ref']==self.reftime]


        try:
            nf = xr.open_dataset(self.targetfile)
            li=li[~li.index.isin(nf.time.values)]
            nf.close
        except FileNotFoundError: 
            pass

        return li
       #return li.head(3*3)
       
    def close(self):
        try:
            self.ftp.close()
        except Exception:
            pass

def ingest(params):
    # 1) Setup del crawler
   
    crw=Crawler(**params)
    
    if params['verbose'] > 0: print ( "Nuove elaborazioni trovate:\n"+"\n".join(map(str,crw.new_dates)))

    # 2) Creazione del targetfile

    ncm=datamaps.NCMangler(**params)

    # 3) riempimento del taghetfile, per ogni data:
    li=crw.appenduri
    for d in crw.new_dates:

        # 3.1) recupera i files raw

        files={}

        try:

            f=li[li['tipo']=='NS'].loc[d]['file']
            files['fileEW']=crw.open(f)
            f=li[li['tipo']=='EW'].loc[d]['file']
            files['fileNS']=crw.open(f)
            f=li[li['tipo']=='CORR'].loc[d]['file']
            files['fileCORR']=crw.open(f)

        except KeyboardInterrupt:
            crw.fix(f)
            crw.close()
            ncm.close()
            return

        # 3.2) appendili al file netcdf
        ncm.coalesce_files(time=d,**files)

    ncm.close()
    crw.close()

