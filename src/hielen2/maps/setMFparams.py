#!/usr/bin/python

	# imgfile <image filename: MANDATORY>
	# outmapf <output mapfile, absolute or relative (to the running script) path and filename: MANDATORY>
	# bands <image processing bands; defaults to '1, 2, 3'> 
	# scale1 <image first band (red or B/W) processing scale (min,max); defaults to '0,255' in case of RGB and to '0,65536' in case of B/W>
	# scale2 <image second band (green) processing scale (min,max); defaults to '0,255'>
	# scale3 <image third band (blue) processing scale (min,max); defaults to '0,255'>
	# crs <image CRS projection (EPSG number); defaults to '3857'>
	# lyrext <image extent (minX, minY, maxX, maxY); defaults to '-20026376.39 -20048966.10 20026376.39 20048966.10'	(= fullext EPSG:3857)>
	# datadir <raster image data directory, relative to mapfile location; defaults to '../data'>
	# inmapf <input mapfile, absolute or relative (to the running script) path and filename; defaults to 'SAGraster.map'>
	# um <unit of measurement ('METERS', 'DD' ...); defaults to 'METERS'>

import mappyfile

def setMFparams(imgfile, outmapf, bands='', scale1='', scale2='', scale3='', crs=3857, lyrext='', datadir='', inmapf='', um=''):

	if ( bands == '' ): 
		bands = '1,2,3'
	if ( scale1 == '' ):
		if ( bands == '1' or bands == '2' or bands == '3' ): 
			scale1='0,65536'
		else:
			scale1='0,255'
	if ( scale2 == '' ):
		scale2='0,255'
	if ( scale3 == '' ):
		scale3='0,255'
	if (lyrext == ''):
		lyrext='-20026376.39 -20048966.10 20026376.39 20048966.10'
	if ( datadir == '' ):
		datadir='../data'
	iif ( inmapf == ''):
		inmapf='SAGraster'
	if ( um == '' ):
		um='METERS'
	
	mapfile = mappyfile.open(inmapf)

	mapfile["shapepath"] = datadir

	mapfile["web"]["metadata"]["ows_onlineresource"] = "http://" + outmapf + "&"

	layers = mapfile["layers"]

	layer = layers[0]

	layer["data"] = [imgfile]
	# oppure
	# layer["data"][0] = imgfile

	layer["processing"] = ['BANDS=' + bands, 'SCALE_1=' + scale1, 'SCALE_2=' + scale2, 'SCALE_3=' + scale3]

	layer["projection"] = "init=epsg:" + str(crs)

	layer["units"] = um

	layer["metadata"]["ows_srs"] = "EPSG:" + str(crs)

	layer["metadata"]["ows_extent"] = lyrext

	mappyfile.save(mapfile, outmapf, 2)

