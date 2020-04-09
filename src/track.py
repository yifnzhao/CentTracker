#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:16:50 2020
@filename: track.py
@author: yifan
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rc('figure',  figsize=(10, 6))
import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience
import os
import pims
import trackpy as tp
import preprocess
from register import combine, register
os.chdir('/Users/yifan/Dropbox/ZYF/dev/GitHub/automated-centrosome-pairing/data/2018-01-17_GSC_L4_L4440_RNAi/')
#frames = pims.ImageSequenceND('lr/*.tif', axes_identifiers = ['t', 'z'])
#frames.bundle_axes = ['z', 'y', 'x']
#frames.iter_axes = 't'
#features = tp.locate(frames[5], diameter=(5, 5, 5), minmass = 10, noise_size = 3)

xml_path = 'u_germline.xml'
tiff_path = 'u_germline.tif'
#initialize
mySpotsPairer = preprocess.pairer()
# merge
mySpotsPairer.merge(xml_path)
# find true pairs
f = mySpotsPairer.findTruePair(verbose = False)
f['z'] = f['Z_UM'] * 2.0
f['y'] = f['Y_UM'] * 5.5
f['x'] = f['X_UM'] * 5.5
f['frame'] = f['t']
linked = tp.link_df(f, 1.0, pos_columns=['X_UM', 'Y_UM', 'Z_UM'])

link_dict = {}
for index, row in linked.iterrows():
    trackID = row['particle']
    if trackID in link_dict:
        link_dict[trackID].append(row)
    else: link_dict[trackID] = [row]


duration = max(linked['frame']+1)
trans_dict = dict.fromkeys(range(duration))
for k, v in link_dict.items():
    if len(v) == 1:
        continue # single frame particle
    currSpot = np.asarray((v[0]['x'], v[0]['y']))
    i = 1
    t = v[0]['frame']
    while i < len(v):
        nextSpot = np.asarray((v[i]['x'], v[i]['y']))
        direction = np.subtract(nextSpot,currSpot)
        if trans_dict[int(t+i)] != None:
            trans_dict[int(t+i)].append(direction)
        else:
            trans_dict[int(t+i)] = [direction]
        currSpot = nextSpot
        i+=1

for k, v in trans_dict.items():
    if v != None:
        v = np.asarray(v)
        trans_dict[k] = np.mean(v, axis = 0)

trans_mat = [(0,0)]
t = 1
while t < duration:
    last_x, last_y = trans_mat[-1]
    direction = trans_dict[t]
    if direction is not None:
        print(1)
        x, y = direction
        trans_mat.append((last_x+x, last_y+y))
    else:
        trans_mat.append((last_x,last_y))
    t+=1
trans_mat = np.array(trans_mat).astype(int)
true_trans_mat = np.array(combine(n_csv=2)) * 3

metadata = register('u_germline.tif', trans_mat, highres = True, compress = 1)





