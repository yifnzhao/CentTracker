#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 10:13:00 2020

@author: yifan
"""
from utils.TrackPairer import pair
from utils.TransMatGenerator import generateTransMat
from utils.register import register
import os
import pickle
class centracker(object):
    def __init__(self,path,originalXML,originalMovie):
        # import model
        self.clf = pickle.load(open('./model/myModel.sav', 'rb'))
        self.path = path
        self.originalXML = originalXML
        self.originalMovie = originalMovie
        self.trans_mat = None
        os.chdir(self.path)
        
    def generateTransMat(self,maxIntensityRatio=0.2,maxDistPair=11,
                    maxDistPairCenter=11,method='Mode',searchRange=2.0):
        
        self.trans_mat = generateTransMat(maxIntensityRatio=maxIntensityRatio,
                                     maxDistPair=maxDistPair,
                                     maxDistPairCenter=maxDistPairCenter,
                                     xml_path=self.originalXML,
                                     tiff_path=self.originalMovie,
                                     method=method,
                                     searchRange=searchRange)
        return self.trans_mat

    def register(self,transmat,highres=True,compress=1,pad=True):
        metadata = register(self.originalMovie,transmat,highres=highres,compress=compress,pad=pad)
        return metadata
    
    def pair(self,registeredXML,maxdist=11,maxcongdist=4,minoverlap=10,dim=None):
        pair(self.path,self.clf,maxdist=maxdist,maxcongdist=maxcongdist,minoverlap=minoverlap,
                     xml_path=registeredXML,dim=None,raw_tiff_path=self.originalMovie)
        


