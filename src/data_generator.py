#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 19:29:46 2020
@filename: data_generator
@author: yifan
"""
import os
import numpy as np
import pandas as pd
from scipy.spatial import distance
from xml_parser import parseTracks, parseSpots
import matplotlib.pyplot as plt
from preprocess import spot
from statistics import mean

class edge(object):
    def __init__(self):
        self.source = None
        self.target = None
        self.track_id = None
        self.t = None
        

class track(object):
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.id = None
        self.t_i = None
        self.t_f = None
        self.t = None
        self.nbr = []
        self.dist = None
        self.overlap = None

class pairer(object):
    def __init__(self, xml):
        self.xml_path = xml
        self.min_overlap = 10
        self.max_dist = 30 # 7-8 microns
        self.truePairs = []
        self.falsePairs = []
        self.allTracks = {}
        self.allSpots = {}
        self.allEdges = {}
        
    def getAllTracks(self):
        track_general, track_detail = parseTracks(self.xml_path)
        #populate the track objects
        for index, row in track_general.iterrows():
            myTrack = track()
            myTrack.id = float(row['TRACK_ID'])
            myTrack.x = float(row['TRACK_X_LOCATION'])
            myTrack.y = float(row['TRACK_Y_LOCATION'])
            myTrack.z = float(row['TRACK_Z_LOCATION'])
            myTrack.t_i = float(row['TRACK_START'])
            myTrack.t_f = float(row['TRACK_STOP'])
            myTrack.t = float(row['TRACK_DURATION'])
            self.allTracks[myTrack.id] = myTrack
            
        for index, row in track_detail.iterrows():
            myEdge = edge()
            myEdge.source = float(row['SPOT_SOURCE_ID'])
            myEdge.target = float(row['SPOT_TARGET_ID'])
            myEdge.track_id = float(row['TRACK_ID'])
            myEdge.t = float(int(row['EDGE_TIME'])) # round to nearest int
            if myEdge.track_id in self.allEdges:
                self.allEdges[myEdge.track_id][myEdge.t] = myEdge.source
            else:
                self.allEdges[myEdge.track_id] = {myEdge.t: myEdge.source}
        return self.allTracks
    
    def getAllSpots(self):
        spots = parseSpots(self.xml_path)
        #populate the track objects
        for index, row in spots.iterrows():
            mySpot = spot()
            mySpot.id = float(row['ID'])
            mySpot.x = float(row['POSITION_X'])
            mySpot.y = float(row['POSITION_Y'])
            mySpot.z = float(row['POSITION_Z'])
            self.allSpots[mySpot.id] = mySpot
        return self.allSpots
    

    
    def findDist(self, id_i, id_j, plot = False):
        
        x = []
        y = []
        trackI = self.allTracks[id_i]
        trackJ = self.allTracks[id_j]
        start = max([trackI.t_i,trackJ.t_i ])
        stop = min([trackI.t_f, trackJ.t_f])
        if stop - start <= 0:
            return
        t = start 
        while t < stop :    

 
            # calculate spindleLength
            # find ids of spots from i, j
            if t not in self.allEdges[trackI.id]:
                t+=1
                continue
            if t not in self.allEdges[trackJ.id]:
                t+=1
                continue
            spot_i = self.allEdges[trackI.id][t]
            spot_j = self.allEdges[trackJ.id][t]
#            print(spot_j)
            # find spot loc
            ix = self.allSpots[spot_i].x
            iy = self.allSpots[spot_i].y
            iz = self.allSpots[spot_i].z
            jx = self.allSpots[spot_j].x
            jy = self.allSpots[spot_j].y
            jz = self.allSpots[spot_j].z
            dist = distance.euclidean((ix,iy,iz),(jx,jy,jz))
                                         
            x.append(t)
            y.append(dist)
            t += 1
        if plot == True:    
            plt.plot(x, y)
            plt.title(str(int(id_i)) + "-" + str(int(id_j)))
        
            plt.savefig(str(int(id_i)) + "-" + str(int(id_j)) + '.png')
            plt.show()
        return y # dist
  

        
    
    def findNeighbors(self):
        f = open("console.txt", "w")
        self.allTracks = self.getAllTracks()   
        self.allSpots = self.getAllSpots()
        # find neighbors by filtering
        for myTrack in self.allTracks.values():
            
            for nbr in self.allTracks.values():
                
                if myTrack.id == nbr.id: # self
                    continue
                
                # find period of overlap: if less than 10 frames, discard
                
                t_start = max([myTrack.t_i, nbr.t_i])
                t_stop = min([myTrack.t_f, nbr.t_f])
                
                if t_stop - t_start < self.min_overlap:
                    f.write(str(int(myTrack.id)) + ' and ' + str(int(nbr.id)) + ' not pair because time\n')
                    continue
                
                # find distance: if more than 20 microns, discard
                
                dist = mean(self.findDist(myTrack.id, nbr.id))
                
                if dist > self.max_dist:
                    f.write(str(int(myTrack.id)) + ' and ' + str(int(nbr.id)) + ' not pair because avg dist\n')
                    continue
                
                #plot
                self.findDist(myTrack.id, nbr.id, plot = True)
                pair = input('Is this a pair? (y/n)')
                if pair == 'y':    
                    myTrack.nbr.append(nbr.id)
                    myTrack.overlap = t_stop - t_start
                    myTrack.dist = dist
                    self.truePairs.append((myTrack.id, nbr.id))
                else:
                    self.falsePairs.append((myTrack.id, nbr.id))
                    
            
            
os.chdir("../data/0716/")
xml_path = 'GT-C2-2018-07-16_GSC_L4_L4440_RNAi_T0.xml'


# parse trackmate output xml
#spots_path = xml_path[:-4] + '_spots.csv'

#spots = parseSpots(xml_path) # get a spots df
#spots.to_csv(path_or_buf= spots_path, index=False) # write spots info to csv

#track_general, track_detail = parseTracks(xml_path)

myPairer = pairer(xml_path)
myPairer.findNeighbors()
true = myPairer.truePairs
false = myPairer.falsePairs
allTracks = myPairer.allTracks
allEdges = myPairer.allEdges
allSpots = myPairer.allSpots



