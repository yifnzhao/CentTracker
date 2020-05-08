#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 18:04:41 2020

@author: yifan
"""
from model.centracker import centracker

# declare paths
originalMovie = 'u_germline.tif'
originalXML = 'u_germline.xml'
path = '/Users/yifan/Dropbox/ZYF/dev/GitHub/centracker/data/2018-01-16_GSC_L4_L4440_RNAi/'

# initialize centracker
myTracker = centracker(path,originalXML,originalMovie)

# generate translation matrix
transmat = myTracker.generateTransMat(maxIntensityRatio=0.2,maxDistPair=11,
                    maxDistPairCenter=11,method='Mode',searchRange=2.0)

# register the movie
metadata = myTracker.register(transmat,highres=True,compress=1,pad=True)

# suppose after the xml output from TrackMate has been generated...TODO
registeredXML = 'r_germline.xml'
# pair the tracks
myTracker.pair(registeredXML,maxdist=11,maxcongdist=4,minoverlap=10,dim=None)
print("All done!")
    
        