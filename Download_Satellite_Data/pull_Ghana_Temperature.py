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
import csv

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
    # Perhaps task.cancel() at some point.
    time.sleep(10)
  print 'Done.', task.status()




#locations = pd.read_csv('locations_major.csv')


# Transforms an Image Collection with 1 band per Image into a single Image with items as bands
# Author: Jamie Vleeshouwer

def appendBand(current, previous):
    # Rename the band
    previous=ee.Image(previous)
    current = current.select([0,4])
    # Append it to the result (Note: only return current item on first element/iteration)
    accum = ee.Algorithms.If(ee.Algorithms.IsEqual(previous,None), current, previous.addBands(ee.Image(current)))
    # Return the accumulation
    return accum

#county_region = ee.FeatureCollection('ft:18Ayj5e7JxxtTPm1BdMnnzWbZMrxMB49eqGDTsaSp')

imgcoll = ee.ImageCollection('MODIS/MYD11A2') \
    .filterBounds(ee.Geometry.Rectangle(-3, 5,-0.02, 11))\
    .filterDate('2013-12-31','2015-12-31')
img=imgcoll.iterate(appendBand)
img=ee.Image(img)

offset = 0.11
scale  = 500
crs='EPSG:4326'

#Algorithm to divide Ghana into grids of equal length
minLon,minLat = -3,5
maxLon,maxLat = -0.02,11

ghLonRange,ghLatRange = 2.98,6
bbLonRange,bbLatRange = 0.30,0.2772
count = 1

ogfirst,ogsecond = -2.78,-2.63
ogthird,ogfourth = 10.86,11

first,second = -2.78,-2.63
third,fourth = 10.86,11

grid = '1_'
grid_n = 1
grid_no = 0


with open('Ghana_locations.csv','a') as f:
    writer = csv.writer(f)
    

    while (bbLatRange <= ghLatRange):
        while(second <= ghLonRange):
            region = str([[first,fourth],[first,third],
                          [second,third],[second,fourth]])
            grid_no += 1
            writer.writerow([grid_n,grid_no,first,second])
            try:
                export_oneimage(img, 'Ghana_temperature', grid+str(grid_no), region, scale, crs)
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

print('All done here ')
