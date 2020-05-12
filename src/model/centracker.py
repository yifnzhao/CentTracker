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
    def __init__(self,path):
        # import model
        self.clf = pickle.load(open('./model/myModel.sav', 'rb'))
        self.path = path
        self.out_folder = path+'out/'
        os.chdir(self.path)
        filenames = os.listdir()
        originalXML = 0
        originalMovie = 0
        for f in filenames:
            if f[-3:] == 'xml':
                if f[0] == 'r': continue # TODO: this line skips the xmls that start with 'r' to facillate the batch processing (per Reda's request, may need to change this back for other uses. 
                self.originalXML = f
                self.registeredXML = './out/r_'+f
                originalXML += 1
                print('The original TrackMate xml is found.')
            elif f[-3:] == 'tif':
                self.originalMovie = f
                self.registeredMovie = './out/r_'+f
                self.final_out = './out/r_'+f[:-4]+'.csv'
                originalMovie += 1
                print('The original movie is found.')
        if originalMovie == 0:
            print('FileNotFoundError: original movie not found')
        elif originalMovie > 1:
            print('Ambiguity: more than 1 movie are found. Please only put the original movie in the current working directory.')
        elif originalXML == 0:
            print('FileNotFoundError: original xml not found')
        elif originalXML > 1:
            print('Ambiguity: more than 1 xml are found. Please only put the xml correponding to the original movie in the current working directory.')
        self.trans_mat = None
        try:
            os.mkdir(self.out_folder)
        except FileExistsError:
            print('Warning: Directory ' , self.out_folder , 'already exists')
        
        
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
        metadata = register(self.originalMovie,transmat,self.registeredMovie,highres=highres,compress=compress,pad=pad)
        return metadata
    
    def pair(self,maxdist=11,mindist=4,maxcongdist=4,minoverlap=10,dim=None):
        pair(self.clf,self.registeredXML,self.originalMovie,self.final_out,
                 maxdist=maxdist,mindist=mindist,maxcongdist=maxcongdist,minoverlap=minoverlap,dim=dim)
             
             

