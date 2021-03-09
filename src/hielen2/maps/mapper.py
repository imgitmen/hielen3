    # outmapf <output mapfile, absolute or relative (to the running script) path and filename: MANDATORY>
    # bands <image processing bands; defaults to '1, 2, 3'> 
    # scale1 <image first band (red or B/W) processing scale (min,max); defaults to '0,255' in case of RGB and to '0,65536' in case of B/W>
    # scale2 <image second band (green) processing scale (min,max); defaults to '0,255'>
    # scale3 <image third band (blue) processing scale (min,max); defaults to '0,255'>
    # crs <image CRS projection (EPSG number); defaults to '3857'>
    # lyrext <image extent (minX, minY, maxX, maxY); defaults to '-20026376.39 -20048966.10 20026376.39 20048966.10'    (= fullext EPSG:3857)>
    # datadir <raster image data directory, relative to mapfile location; defaults to '../data'>
    # inmapf <input mapfile, absolute or relative (to the running script) path and filename; defaults to 'SAGraster.map'>
    # um <unit of measurement ('METERS', 'DD' ...); defaults to 'METERS'>

import mappyfile
import re
from hielen2 import conf

def setMFparams(
        outmapf, 
        bands=3, 
        scale=['0,255','0,255','0,255'], 
        crs='EPSG:3857', 
        lyrext='-20026376.39 -20048966.10 20026376.39 20048966.10',
        datadir='', 
        inmapf=conf['maptemplate'], 
        um='METERS',
        ows_onlineresources="http://pippo&"
        ):

    mapfile = mappyfile.open(inmapf)
    mapfile["shapepath"] = datadir
    mapfile["web"]["metadata"]["ows_onlineresource"] = ows_onlineresources

    if ( bands == 1 ):
        scale=['0,65536']

    layer = mapfile["layers"][0]

    tbands=','.join(map(str,(range(1,bands+1))))
    layer['processing']=[f'BANDS={tbands}']

    for i in range (0,bands):
        layer['processing'].append(f"SCALE_{i+1}={scale[i]}")

    layer["projection"] = f"init={str(crs).lower()}"

    layer["units"] = re.sub('METRES?','METERS',um.upper())

    layer["metadata"]["ows_srs"] = str(crs).upper()

    layer["metadata"]["ows_extent"] = lyrext

    mappyfile.save(mapfile, outmapf, 2)

