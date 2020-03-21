#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 19:29:46 2020
@filename: track_pairer
@author: yifan
"""
import os
import numpy as np
import pandas as pd
from scipy.spatial import distance
from xml_parser import parseTracks, parseSpots
import matplotlib.pyplot as plt
from preprocess import spot
from statistics import mean, stdev
from skimage.external import tifffile
from register import combine_roi, roi2mat
import pickle

def normalize(vector):
    # unpack
    x, y, z = vector
    # calculate length
    length = (x**2 + y**2 + z**2)**0.5
    # divide by length
    return (x/length, y/length, z/length)

def findCong(time, dist, max_dist = 6):
    t_cong = 0
    t_prev = time[0]-1
    all_periods = []
    for t, d in zip(time, dist):
        if t_prev + 1 != t: # not continuous
            if t_cong != 0:
                all_periods.append(t_cong)
            t_cong = 0
        if (d < max_dist):
            t_cong += 1
        t_prev = t 
    all_periods.append(t_cong)
    return max(all_periods)
        
        
        

class cell(object):
    def __init(self):
        self.centID_i = None # track object, i
        self.centID_j = None # track object, j
        self.t_overlap = None 
        self.t_cong = 0 # congression, continuous time duration under 5 micron
        self.sl_i = None # spindle length initial
        self.sl_f = None # spindle length final
        self.sl_min = None # minimum spindle length
        self.sl_max = None # maximum spindle length
        self.center = None # xyz coords of center
        self.center_stdev = None
        self.normal_stdev = None
        self.dist_center_to_border # dist from the center of cell to closest tiff border

        
        

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
        self.duration = None


class pairer(object):
    def __init__(self, xml, translation_matrix):
        self.xml_path = xml
        self.min_overlap = 10
        self.max_dist = 30 # 7-8 microns
        self.trans_mat = translation_matrix
        self.nbrTracks = []
        self.allTracks = {}
        self.allSpots = {}
        self.allEdges = {}
        self.cells = []
        
    def getAllTracks(self):
        # read from xml all info about tracks
        track_general, track_detail = parseTracks(self.xml_path)
        # populate the track objects
        for index, row in track_general.iterrows():
            myTrack = track()
            myTrack.id = int(row['TRACK_ID'])
            myTrack.x = float(row['TRACK_X_LOCATION'])
            myTrack.y = float(row['TRACK_Y_LOCATION'])
            myTrack.z = float(row['TRACK_Z_LOCATION'])
            myTrack.t_i = float(row['TRACK_START'])
            myTrack.t_f = float(row['TRACK_STOP'])
            myTrack.duration = float(row['TRACK_DURATION'])
            self.allTracks[myTrack.id] = myTrack
            
        for index, row in track_detail.iterrows():
            myEdge = edge()
            myEdge.source = int(row['SPOT_SOURCE_ID'])
            myEdge.target = int(row['SPOT_TARGET_ID'])
            myEdge.track_id = int(row['TRACK_ID'])
            myEdge.t = float(int(row['EDGE_TIME'])) # round to nearest int
            if myEdge.track_id in self.allEdges:
                self.allEdges[myEdge.track_id][myEdge.t] = myEdge.source
            else:
                self.allEdges[myEdge.track_id] = {myEdge.t: myEdge.source}
        return self.allTracks
    
    def getAllSpots(self):
        spots = parseSpots(self.xml_path)
        # populate the track objects
        for index, row in spots.iterrows():
            mySpot = spot()
            mySpot.id = int(row['ID'])
            mySpot.x = float(row['POSITION_X'])
            mySpot.y = float(row['POSITION_Y'])
            mySpot.z = float(row['POSITION_Z'])
            self.allSpots[mySpot.id] = mySpot
        return self.allSpots
    

    
    def findDist(self, id_i, id_j, plot = False):
        '''
        finds the distance between two tracks over time
        input: id_i and id_j are track id's
        '''
        # x,y for plotting purpose
        time = [] # list of time
        sl = [] # list of corresponding distance 
        centers = {'x': [], 'y':[], 'z': []}
        normals = {'x': [], 'y':[], 'z': []}
        #get track objects by id
        trackI = self.allTracks[id_i]
        trackJ = self.allTracks[id_j]
        #find start and stop time (overlapped between two tracks)
        start = max([trackI.t_i,trackJ.t_i])
        stop = min([trackI.t_f, trackJ.t_f])
        if stop - start <= 0:
            return
        t = start 
        
        while t < stop :    

            # calculate spindleLength
            # find ids of spots from i, j
            if t not in self.allEdges[trackI.id]: 
                # note: allEdges[trackI.id] is a dict, k is time, v is spot_id
                t+=1
                continue
            if t not in self.allEdges[trackJ.id]:
                t+=1
                continue
            # get spot id
            spot_i = self.allEdges[trackI.id][t]
            spot_j = self.allEdges[trackJ.id][t]
            # find spot loc by spot id
            ix = self.allSpots[spot_i].x
            iy = self.allSpots[spot_i].y
            iz = self.allSpots[spot_i].z
            jx = self.allSpots[spot_j].x
            jy = self.allSpots[spot_j].y
            jz = self.allSpots[spot_j].z
            dist = distance.euclidean((ix,iy,iz),(jx,jy,jz))
            center = ((ix+jx)/2, (iy+jy)/2, (iz+jz)/2)
            normal = ((ix-jx), (iy-jy), (iz-jz))
            # normalized normal vector
            n_normal = normalize(normal)
    
            time.append(t)
            sl.append(dist)
            centers['x'].append(center[0])
            centers['y'].append(center[1])
            centers['z'].append(center[2])
            normals['x'].append(n_normal[0])
            normals['y'].append(n_normal[1])
            normals['z'].append(n_normal[2])
            t += 1
            
        if plot == True:    
            plt.plot(time, sl)
            plt.title(str(int(id_i)) + "-" + str(int(id_j)))
        
            plt.savefig(str(int(id_i)) + "-" + str(int(id_j)) + '.png')
            plt.show()
        return sl, centers, normals, time
          
    def find_dist_center_to_border(self):
        '''
        Finds the distance of cell center to the closest border
        - im: unregistered tiff
        - trans_mat
        '''
        with tifffile.TiffFile('u_germline.tif') as tif:    
            tif_tags = {}
            for tag in tif.pages[0].tags.values():
                name, value = tag.name, tag.value
                tif_tags[name] = value
                
        translation = np.array(self.trans_mat).astype(int)
        
        # search for extrema  
        x_low , y_low = 0, 0
        x_dim, y_dim = tif_tags['image_width'], tif_tags['image_length']
        for t in range(len(translation)): 
            trans_x, trans_y = translation[t]
            if trans_y < y_low:
                y_low = trans_y
            if trans_x < x_low:
                x_low = trans_x       
                
        for myCell in self.cells:          
            # unpack cell_center
            x, y, z = myCell.center
            # find original coords (before registration)
            adj_x, adj_y = x+x_low, y+y_low
            toTop = adj_y
            toBottom = y_dim - adj_y
            toLeft = adj_x
            toRight = x_dim - adj_x
            myCell.dist_center_to_border = min([toTop, toBottom, toLeft, toRight])
        
    def findNeighbors(self):
        f = open("console.txt", "w")
        # 1. tracks and edges bookkeeping
        self.allTracks = self.getAllTracks()
        # 2. spots bookkeeping
        self.allSpots = self.getAllSpots()
        # 3. find neighbors by crude filters
        
        for myTrack in self.allTracks.values():
             # 1) if track duration less than 10, out
            if myTrack.duration < self.min_overlap:
                f.write(str(int(myTrack.id)) + ' excluded: track too short\n')
                continue
            
            for nbr in self.allTracks.values():
            
                # 1) if track duration less than 10, out
                if nbr.duration < self.min_overlap:
                    continue
                # 2)  myTrack is the same track as nbr, out
                elif myTrack.id == nbr.id:
                    continue
                # 3) find period of overlap: if less than 10 frames, out
                t_start = max([myTrack.t_i, nbr.t_i])
                t_stop = min([myTrack.t_f, nbr.t_f])
                if t_stop - t_start < self.min_overlap:
                    f.write(str(int(myTrack.id)) + ' and ' + str(int(nbr.id)) + ' not pair: overlap time too short\n')
                    continue
                # 4) find avg distance: if greater than 20 microns, out
                dist, centers, normals, time = self.findDist(myTrack.id, nbr.id)
                avg_dist = mean(dist)
                if avg_dist > self.max_dist:
                    f.write(str(int(myTrack.id)) + ' and ' + str(int(nbr.id)) + ' not pair: too far away\n')
                    continue
                # filtering finished, fill in cell info
                myCell = cell()
                myCell.centID_i = myTrack.id
                myCell.centID_j = nbr.id
                myCell.t_overlap = t_stop - t_start
                myCell.sl_i = dist[0]
                myCell.sl_f = dist[-1]
                myCell.sl_max = max(dist)
                myCell.sl_min = min(dist)
                myCell.center = (mean(centers['x']), mean(centers['y']), mean(centers['z']))
                stdev_x = stdev(centers['x'])
                stdev_y = stdev(centers['y'])
                stdev_z = stdev(centers['z'])
                stdev_x_n = stdev(normals['x'])
                stdev_y_n = stdev(normals['y'])
                stdev_z_n = stdev(normals['z'])
                myCell.center_stdev = (stdev_x**2 + stdev_y**2 + stdev_z**2)**0.5
                myCell.normal_stdev = (stdev_x_n**2 + stdev_y_n**2 + stdev_z_n**2)**0.5
                myCell.t_cong = findCong(time, dist)
                self.cells.append(myCell)
                #plot
                #self.findDist(myTrack.id, nbr.id, plot = True)
        
        self.find_dist_center_to_border()
        
        return self.cells

def cell2df(cells):
    myDict = {'center_stdev': [],
              'dist_center_to_border': [],
              'normal_stdev': [],
              'sl_f': [],
              'sl_i': [],
              'sl_max': [],
              'sl_min': [],
              't_cong': [],
              't_overlap': [],
              'centID_i': [],
              'centID_j': []}
    for myCell in cells:
        myDict['center_stdev'].append(myCell.center_stdev)
        myDict['dist_center_to_border'].append(myCell.dist_center_to_border)
        myDict['normal_stdev'].append(myCell.normal_stdev)
        myDict['sl_f'].append(myCell.sl_f)
        myDict['sl_i'].append(myCell.sl_i)
        myDict['sl_max'].append(myCell.sl_max)
        myDict['sl_min'].append(myCell.sl_min)
        myDict['t_cong'].append(myCell.t_cong)
        myDict['t_overlap'].append(myCell.t_overlap)
        myDict['centID_i'].append(myCell.centID_i)
        myDict['centID_j'].append(myCell.centID_j)
    df = pd.DataFrame(myDict)
    return df
        
if __name__ == "__main__":
    os.chdir("../data/2018-01-17_GSC_L4_L4440_RNAi/")
    xml_path = 'r_germline.xml'
    
    #--below for 0716 folder----------------
    #trans_mat = pd.read_csv("ROI.csv", header = None)
    #trans_mat = roi2mat(trans_mat)
    #########################################
    #--below for 0116, 0117 folder-----------
    mat1 = pd.read_csv("1.csv", header = None)
    mat1 = roi2mat(mat1)
    mat2 = pd.read_csv("2.csv", header = None)
    mat2 = roi2mat(mat2)
    trans_mat = combine_roi(mat1, mat2)
    #########################################
    trans_mat = trans_mat * 3
    
    # crude pairer, generate features
    myPairer = pairer(xml_path, trans_mat)
    cells = myPairer.findNeighbors()
    df = cell2df(cells)
    df.to_csv ('features.csv', index = False, header=True)
    
    # generate features panel for ml clf
    X_df = pd.read_csv('features.csv', usecols = range(9))
    X = X_df.to_numpy()
    # load the model from disk
    clf = pickle.load(open('../ML/myModel.sav', 'rb'))
    # predict
    y_pred = clf.predict(X)
    df['Predicted_Label'] = y_pred
    df.to_csv ('predictions.csv', index = False, header=True)




