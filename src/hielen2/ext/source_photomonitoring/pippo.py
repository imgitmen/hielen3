#!/usr/bin/env python
# coding=utf-8
import os
import io
import PIL
import pandas as pd

import rendering


dataset=rendering.Render(targetfile='../../../var/cache/esempio/20200101102000/master.nc', background=None, gridratio=10)
timestamp=dataset.timeline[-1]
timeref=dataset.reftime
width
height
x_offset
y_offset

imgarray=dataset.generate_map(timestamp=timestamp,timeref=timeref)
result = PIL.Image.fromarray(imgarray)
img = PIL.Image.new(result.mode, (width, height), (0,0,0,0))
img.paste(result, x_offset,y_offset)
img.save('prova.png', format='PNG') 

