#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 18:04:41 2020

@author: yifan
"""
from model.centracker import centracker
import os
import pickle
# declare paths
path = '/Users/yifan/Dropbox/ZYF/dev/centracker_local/data/abrupt/'


(_,foldernames,_) = next(os.walk(path))
methods = ['Mean', 'Mode', 'Median']
search_range = [2,5,10,20]
for folder in foldernames:
    
    # initialize centracker
    myTracker = centracker(path+folder+'/')
    for m in methods:
        for r in search_range:
        # generate translation matrix
            transmat = myTracker.generateTransMat(maxIntensityRatio=0.2,maxDistPair=11,
                        maxDistPairCenter=11,method=m,searchRange=r)
            with open('transmat_method_{}_range_{}'.format(m,r), 'wb') as f:
                pickle.dump(transmat,f)
            print('transmat_method_{}_range_{}'.format(m,r), 'saved')
            