#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 27 01:52:57 2021

@author: yifan
"""

## import necessary packages and utility functions
import sys
sys.path.append('../src/')
from utils import *
import os
import pickle
root = '../data/'
movie_name = '2018-01-17_GSC_L4_L4440_RNAi-long'
## specify file paths related to track pairing
model_path = 'myModel_07042021.sav'
originalMovie = '{}/{}/{}.tif'.format(root,movie_name,movie_name)
registeredXML = '{}/{}/r_{}.xml'.format(root,movie_name,movie_name)
out_folder ='{}/{}/'.format(root,movie_name)
out_csv='{}/r_{}.txt'.format(out_folder,movie_name)
out_coords = '{}/r_{}_coords.txt'.format(out_folder,movie_name)
out_cellid = '{}/r_{}_cellIDs.txt'.format(out_folder,movie_name)
## load classifier
model = pickle.load(open(model_path, 'rb'))
# pair the tracks
mypairer=pair(model,registeredXML,originalMovie,out_folder,out_csv,
                 maxdist=100,mindist=4,maxcongdist=4,minoverlap=0)





pred = '/Users/yifan/Dropbox/ZYF/dev/research/centtracker/CentTracker-master/data/2018-01-17_GSC_L4_L4440_RNAi-long/predictions.csv'
pred = pd.read_csv(pred)

train_x = '/Users/yifan/Dropbox/ZYF/dev/research/centtracker/X_updated.csv'
train_y = '/Users/yifan/Dropbox/ZYF/dev/research/centtracker/y.csv'
train_x = pd.read_csv(train_x)
train_y = pd.read_csv(train_y)

train_x['True_Label']=train_y['True_Label']

labeled = train_x[train_x['True_Label']==1]

import matplotlib.pyplot as plt
for k in labeled.columns:
    plt.hist(labeled[k])
    plt.title('labeled {}'.format(k))
    plt.show()
    if k in pred.columns:
        plt.hist(pred[k])
        plt.title('pred {}'.format(k))
        plt.show()
    elif k[:-11] in  pred.columns:
        plt.hist(pred[k[:-11]])
        plt.title('pred {}'.format(k))
        plt.show()
        
        
