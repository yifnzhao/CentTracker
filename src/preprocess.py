#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 19:35:38 2019
@author: yifan
"""

import pandas as pd
import os
from scipy.spatial import distance
from skimage.external import tifffile
from xml_parser import parseTracks, parseSpots
import pickle
import numpy as np
from register import translate
import matplotlib.pyplot as plt


class spot(object):
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.t = None
        self.id = None
        self.raw_int = None
        self.Nbr = None
        self.currLoc = None
        self.sumInt = None
        self.next = None
        self.intRatio = None
        self.dist = None
        self.summinRatio = None
        self.diam = None
        self.maxInt = None
        self.contrast = None
        
        
class pairer(object):
    def __init__(self, maxIntensityRatio = 0.2, maxDistPair = 10, maxDistPairCenter = 10):
        self.max_ratio = maxIntensityRatio
        self.max_dist = maxDistPair
        self.max_dist_center = maxDistPairCenter
        self.spots_merged_df = None
        self.true_pairs = {} # key is time
        self.trans_mat = None

    
    def merge(self, xml_path):
        # parse trackmaet output xml
        spots_path = 'u_spots.csv'
        spots = parseSpots(xml_path)
        spots.to_csv(path_or_buf= spots_path, index=False)
        
        # load coordinate csv file
        coords_df = pd.read_csv(spots_path,
                       usecols = ['ID', 'name' ,'POSITION_X','POSITION_Y', 
                                  'POSITION_Z', 'POSITION_T', 'FRAME'])
        # load intensity csv file
        int_path = 'u_germline_intensity.csv'
        int_df = pd.read_csv(int_path, usecols = ['RawIntDen'])
        
        self.spots_merged_df = pd.concat([coords_df, int_df], sort = False, axis = 1)

        
    def findTruePair(self, verbose = True):

        time_dict = {}
        for index, row in self.spots_merged_df.iterrows():
            if row['FRAME'] in time_dict:
                time_dict[row['FRAME']].append(row)
            else:
                time_dict[row['FRAME']] = [row]
        nbr_list = []
        for t, all_spots_at_t in time_dict.items():
            n_pair = 0
            
            self.true_pairs[t] = []
            
            for this_spot in all_spots_at_t:
                
                self.true_pairs[t]
                mySpot = spot()
                mySpot.t = t
                mySpot.x = this_spot['POSITION_X']
                mySpot.y = this_spot['POSITION_Y']
                mySpot.z = this_spot['POSITION_Z']
                mySpot.t = t
                mySpot.id = this_spot['ID']
                mySpot.raw_int = this_spot['RawIntDen']
                minRatio = self.max_ratio
                minDist =  self.max_dist
                
                for neighbor in all_spots_at_t:
                    
                    if neighbor['ID'] == mySpot.id: # self
                        continue
                    elif neighbor['ID'] in nbr_list: # already paired
                        continue
                    
                    myNeighbor = spot()
                    myNeighbor.t = t
                    myNeighbor.id = neighbor['ID']
                    myNeighbor.x = neighbor['POSITION_X']
                    myNeighbor.y = neighbor['POSITION_Y']
                    myNeighbor.z = neighbor['POSITION_Z']
                    myNeighbor.raw_int = neighbor['RawIntDen']
                  
                    dist = distance.euclidean((mySpot.x, mySpot.y, mySpot.z), 
                                (myNeighbor.x, myNeighbor.y, myNeighbor.z))
                    int_diff_ratio = abs(mySpot.raw_int - myNeighbor.raw_int) / mySpot.raw_int
                    
                    # filtering step
                    if int_diff_ratio <  minRatio:
                        minRatio = int_diff_ratio
                        if dist < minDist:
                            minDist = dist
                            mySpot.Nbr = myNeighbor
                            mySpot.intRatio = int_diff_ratio
                            mySpot.dist = dist
                
                if (mySpot.Nbr != None):
                    
                    mySpot.currLoc = ((mySpot.x + mySpot.Nbr.x)/2, 
                                      (mySpot.y + mySpot.Nbr.y)/2, 
                                      (mySpot.z + mySpot.Nbr.z)/2)
                    mySpot.sumInt = mySpot.Nbr.raw_int + mySpot.raw_int
                    
                    nbr_list.append(mySpot.Nbr.id)
                    self.true_pairs[t].append(mySpot)
                    n_pair+=1
                    
            
            if verbose == True: 
                print('Time = ' + str(t) + ': ' + str(n_pair) + " pairs found.") 
            
        with open('spot_pairs.pkl', 'wb') as f:
            pickle.dump(self.true_pairs, f)
        cell_df = self.cell2df()
        return cell_df
                    
    def cell2df(self):
        cell_list = []
        for time, spots_t in self.true_pairs.items():
            for s in spots_t:
                x,y,z = s.currLoc
                t = time
                sumInt = s.sumInt
                id_i = s.id
                id_j = s.Nbr.id
                sl = s.dist #spindle length
                info = [t,z,y,x,id_i, id_j, sl, sumInt]
                cell_list.append(info)
                
        cell_df = pd.DataFrame(columns=['t','Z_UM','Y_UM','X_UM','ID_I','ID_J','SL_UM','SUMINT'], data=cell_list)
        cell_df.to_csv("cell.csv")
        return cell_df
    
    def link(self, weighted_m = True, verbose = True):
        trans_mat = [np.zeros(2).astype(int)]
        for t0, spots_t0 in self.true_pairs.items():
            x = []
            y = []
            if t0+1 not in self.true_pairs: # last time point
                continue
            spots_t1 = self.true_pairs[t0+1]
            total_dir = [] #t0-t1

            for currSpot in spots_t0:
                
                currLoc = currSpot.currLoc
                currInt = currSpot.sumInt
                
                minRatio = mySpotsPairer.max_ratio
                minDist =  mySpotsPairer.max_dist_center
                
                for nextSpot in spots_t1:
                    nextLoc = nextSpot.currLoc
                    nextInt = nextSpot.sumInt
                    dist = distance.euclidean(currLoc, nextLoc)
                    
                    # search
                    if dist < minDist:
                        intDiffRatio = abs(currInt - nextInt) / currInt
                        if intDiffRatio <  minRatio:
                            minRatio = intDiffRatio
                            currSpot.next = nextSpot
                            currSpot.summinRatio = intDiffRatio
                
                    
                if currSpot.next != None:
                    # find x-y direction vector
                    direction = np.asarray(currSpot.next.currLoc[0:2]) - np.asarray(currSpot.currLoc[0:2])
                    x.append(direction[0])
                    y.append(currSpot.summinRatio)
                    total_dir.append(direction)
            
            if verbose == True: 
                print('Time = ' + str(t0) + ': ' + str(len(total_dir)) + ' links found at current time point.') 
            
            if len(total_dir) == 0:
               avg_dir = np.zeros(2).astype(int)
            else:
                avg_dir = np.asarray(np.mean(np.asarray(total_dir), axis = 0))
            
            
            plt.scatter(x, y)
            plt.show()
            trans_mat.append(avg_dir)
            
        self.trans_mat = [np.zeros(2).astype(int)]
        
        for i in range(len(trans_mat)-1):
            prev = self.trans_mat[-1]
            dirVector = trans_mat[i+1]
            curr = prev + dirVector
            self.trans_mat.append(curr)
        
        self.trans_mat = np.asarray(self.trans_mat)
        with open('trans_mat.pkl', 'wb') as f:
            pickle.dump(self.trans_mat, f)
        
        return self.trans_mat


    def scatter_int_dist(self):
        x = []
        y = []
        for t, spots in self.true_pairs.items():
            for spot in spots:
                x.append(spot.dist)
                y.append(spot.intRatio)
            plt.scatter(x, y)
            plt.title('t = '+ str(t))
            plt.show()
        

if __name__ == '__main__':        
    os.chdir('/Users/yifan/Dropbox/ZYF/dev/GitHub/automated-centrosome-pairing/data/2018-01-17_GSC_L4_L4440_RNAi/')
    xml_path = 'u_germline.xml'
    tiff_path = 'u_germline.tif'
    #initialize
    mySpotsPairer = pairer()
    # merge
    mySpotsPairer.merge(xml_path)
    # find true pairs
    true_pairs = mySpotsPairer.findTruePair(verbose = False)
   
    # get trans_mat
#    trans_mat = mySpotsPairer.link(weighted_m = True, verbose = False)
#    mySpotsPairer.scatter_int_dist()
#
#    ratio_p_um = 8.53
#    ratio_low_res = 1/3
#
#    
#    
    
    
    
#    im_in = tifffile.imread(lr_tiff_path)
#    im_out = translate(im_in, mySpotsPairer.trans_mat, highres = False)
#    with tifffile.TiffWriter('GT-' + lr_tiff_path, bigtiff=True) as tif:
#        for i in range(im_out.shape[0]):
#            tif.save(im_out[i], compress = 6)

#    im_in = tifffile.imread(tiff_path)
#    im_out = translate(im_in, mySpotsPairer.trans_mat, highres = True, compress = ratio_p_um * ratio_low_res )
#    with tifffile.TiffWriter('GT-' + tiff_path, bigtiff=True) as tif:
#        for i in range(im_out.shape[0]):
#            tif.save(im_out[i], compress = 6)


