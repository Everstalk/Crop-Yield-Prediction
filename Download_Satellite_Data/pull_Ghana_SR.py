"""
Michael D. Saneke
Capstone Applied Project
"""

import ee
import time
import sys
import numpy as np
import pandas as pd
import itertools
import os
import urllib
import traceback

ee.Initialize()

def export_oneimage(img,folder,name,region,scale,crs):
  task = ee.batch.Export.image(img, name, {
      'driveFolder':folder,
      'driveFileNamePrefix':name,
      'region': region,
      'scale':scale,
      'crs':crs
  })
  task.start()
  while task.status()['state'] == 'RUNNING':
    print 'Running...'

    time.sleep(10)
  print 'Done.', task.status()




#locations = pd.read_csv('locations_remedy.csv')


# Transforms an Image Collection with 1 band per Image into a single Image with items as bands
# Author: Jamie Vleeshouwer

def appendBand(current, previous):
    # Rename the band
    previous=ee.Image(previous)
    current = current.select([0,1,2,3,4,5,6])
    # Append it to the result (Note: only return current item on first element/iteration)
    accum = ee.Algorithms.If(ee.Algorithms.IsEqual(previous,None), current, previous.addBands(ee.Image(current)))
    # Return the accumulation
    return accum

#county_region = ee.FeatureCollection('ft:18Ayj5e7JxxtTPm1BdMnnzWbZMrxMB49eqGDTsaSp')

imgcoll = ee.ImageCollection('MODIS/MOD09A1') \
    .filterBounds(ee.Geometry.Rectangle(-3, 5,-0.02, 11))\
    .filterDate('2002-12-31','2016-8-4')
img=imgcoll.iterate(appendBand)
img=ee.Image(img)

img_0=ee.Image(ee.Number(-100))
img_16000=ee.Image(ee.Number(16000))

img=img.min(img_16000)
img=img.max(img_0)

# img=ee.Image(ee.Number(100))
# img=ee.ImageCollection('LC8_L1T').mosaic()


offset = 0.11
scale  = 500
crs='EPSG:4326'
grid = '1_'
grid_no = 0


#Grid Algorithm
minLon,minLat = -3,5
maxLon,maxLat = -0.02,11

ghLonRange,ghLatRange = 2.98,6
bbLonRange,bbLatRange = 0.30,0.2772
count = 1

ogfirst,ogsecond = -2.78,-2.63
ogthird,ogfourth = 10.86,11

first,second = -2.78,-2.63
third,fourth = 10.86,11

while (bbLatRange <= ghLatRange):
    while(second <= ghLonRange):
        region = str([[first,fourth],[first,third],
                      [second,third],[second,fourth]])
        grid_no += 1
        try:
            export_oneimage(img, 'Ghana_images', grid+str(grid_no), region, scale, crs)
            first = second
            second = first + 0.2772
        except:
            print('retry')
            traceback.print_exc()
            time.sleep(1)
            continue

    bbLatRange += 0.2772
    count += 1
    first = ogfirst
    second = ogsecond
    third = ogthird * count
    fourth = ogfourth * count

    while True:
        try:
            export_oneimage(img, 'Ghana_images', fname, region, scale, crs)
        except:
            print 'retry'
            time.sleep(10)
            continue
        break

print("All Done Here")
