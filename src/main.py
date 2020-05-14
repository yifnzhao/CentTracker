#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 18:04:41 2020

@author: yifan
"""
from model.centracker import centracker

# declare paths
path = '/Users/yifan/Dropbox/ZYF/dev/centracker_local/data/trial_in/'
out_path = '/Users/yifan/Dropbox/ZYF/dev/centracker_local/data/trial_out/'

# initialize centracker
myTracker = centracker(path,out_path)
#
## generate translation matrix
#transmat = myTracker.generateTransMat(maxIntensityRatio=0.2,maxDistPair=11,
#                    maxDistPairCenter=11,method='Mode',searchRange=2.0,tbb_ch=1)
#
## register the movie
#metadata = myTracker.register(transmat,highres=True,compress=1,pad=True)
#
## suppose after the xml output from TrackMate has been generated...TODO
#while 1:
#    cont = input("Checkpoint: Has the registered movie been processed through TrackMate? (y/n) ")
#    if cont == 'y':
#        break
# pair the tracks
myTracker.pair(maxdist=11,maxcongdist=4,minoverlap=10,dim=None)
print("All done!")
    
        