#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 19:35:38 2019
@author: yifan
"""

import pandas as pd
import os
from scipy.spatial import distance
from scipy.stats import mode
from skimage.external import tifffile
from utils.xmlParser import parseSpots
import pickle
import numpy as np
import matplotlib.pyplot as plt
import trackpy as tp

############################################
# Implement the batchMeasureIntensity in python
############################################
def batchMeasureIntensity(path,conversion,radius=1,trackmate_xml_path ='u_germline.xml',tiff_path = 'u_germline.tif',output='r_spots_merged.csv'):
    """
    Measures the raw integrated intensity of the spots identified.
    
    - The radius argument is the radius of the "oval" area to be measured
    
    - The conversion argument is a dictionary of pixel to micon conversion for x, y, z
    """
    os.chdir(path)
    spots = parseSpots(trackmate_xml_path) 
    coords = []
    for index, row in spots.iterrows():
        x = float(row['POSITION_X'])/ conversion['x']
        y = float(row['POSITION_Y']) / conversion['y']
        z = float(row['POSITION_Z']) / conversion['z']
        t = row['FRAME']
        my_coord = (int(x),int(y),int(z), int(t))
        coords.append(my_coord)
    radius = int(radius / conversion['x'])
    intensities = []
    with tifffile.TiffFile(tiff_path) as tif:
        # read tiff
        im_in = tif.asarray() #(t,z,y,x)
        n_frame, n_zstep, y_dim, x_dim = im_in.shape
        for X,Y,Z,T in coords:
            # calculate the raw integrated intensity
            intensity = 0
            for x in range(X-radius,X):
                if x < 0: continue
                if x >= x_dim: continue
                for y in range(Y-radius,Y):
                    if y < 0: continue
                    if y >= y_dim: continue
                    intensity+= im_in[T][Z][y][x]
            intensities.append(intensity)
    # merge
    spots['POSITION_X'] = spots['POSITION_X'].astype('float')
    spots['POSITION_Y'] = spots['POSITION_Y'].astype('float')
    spots['POSITION_Z'] = spots['POSITION_Z'].astype('float')
    intensity_df = pd.DataFrame({'RawIntDen':intensities})
    df = pd.concat([spots, intensity_df], sort = False, axis = 1)
    df.to_csv(output)
    return df
############################################
# find the pixel to um conversion using the original tiff
 ############################################
def findConv(tiff_path):
    with tifffile.TiffFile(tiff_path) as tif:
        # read metadata as tif_tags (dict)
        tif_tags = tif.pages[0].tags
        found = 0
        for t in tif_tags.values():
            if t.name == 'x_resolution':
                x_resolution = t.value
                found+=1
            elif t.name == 'y_resolution':
                y_resolution = t.value
                found+=1
            elif t.name == 'image_description':
                description = t.value.split()
                found+=1
            if found == 3:
                break
    for e in description:
        if e[:8] == b'spacing=':
            z = float(e[8:])
            break
    conversion = {'x': x_resolution[1]/x_resolution[0],
                  'y': y_resolution[1]/y_resolution[0],
                  'z': z}   
    return conversion


############################################
# Spot object
############################################
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
        
############################################     
# Spot pairing
############################################
class SpotPairer(object):
    def __init__(self,conversion,maxIntensityRatio=0.2,maxDistPair=11,maxDistPairCenter=11):
        """
        Initializing a spot pairer
        
        - The conversion argument is a dictionary of pixel to micon conversion for x, y, z
        
        - The maxIntensityRatio is a threshold term for percentage difference in intensity
        
        - The maxDistPair is a distance threshold term (in microns) for how far away two spots can be but still counted as a pair
        
        - The maxDistPairCenter is a distance threshold term (in microns) for how far away two cell centers (from different time spots) can be but still counted as the same cell
        """
        self.max_ratio = maxIntensityRatio
        self.max_dist = maxDistPair 
        self.max_dist_center = maxDistPairCenter
        self.spots_merged_df = batchMeasureIntensity('./',conversion,radius=1,
            trackmate_xml_path ='u_germline.xml',tiff_path = 'u_germline.tif',
            output='r_spots_merged.csv')
        self.true_pairs = {} # dict key is time
        self.trans_mat = None
        
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
                if mySpot.raw_int == 0:
                    continue
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


def generateTransMat(maxIntensityRatio=0.2,maxDistPair=11,maxDistPairCenter=11,xml_path='u_germline.xml',tiff_path ='u_germline.tif',method='Mode',searchRange=1.0):
    """
    Generats a translation matrix from trackmate xml output
    - The definition of maxIntensityRatio, maxDistPair, maxDistPairCenter arguments are the same as in the SpotPairer
    
    - The method arugument specifies how the translation vectors between every two continuous time points will be calculated:
        - Mean = Mean value of all direction vectors at the specific time
        - Median = Median value of all direction vectors at the specific time
        - Mode = Mode value of all direction vectors at the specific time
    """
    
    
    #find the pixel to um conversion
    conversion = findConv(tiff_path)
    #initialize
    mySpotsPairer = SpotPairer(conversion,maxIntensityRatio=maxIntensityRatio,
                   maxDistPair=maxDistPair,maxDistPairCenter=maxDistPairCenter)
    #find spot pairs
    f = mySpotsPairer.findTruePair(verbose = False)
    f['z'] = f['Z_UM'] / conversion['z']
    f['y'] = f['Y_UM'] / conversion['y'] 
    f['x'] = f['X_UM'] / conversion['x']
    f['frame'] = f['t']
    linked = tp.link_df(f,searchRange, pos_columns=['X_UM', 'Y_UM', 'Z_UM'])
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
            if method == 'Mean':
                trans_dict[k] = np.mean(v, axis = 0)
            elif method == 'Median':
                trans_dict[k] = np.median(v,axis = 0)
            elif method == 'Mode':
                v=v.astype(int)
                trans_dict[k] = mode(v,axis=0)[0].flatten()
    trans_mat = [(0,0)]
    t = 1
    while t < duration:
        last_x, last_y = trans_mat[-1]
        direction = trans_dict[t]
        if direction is not None:
            x, y = direction
            trans_mat.append((last_x+x, last_y+y))
        else:
            trans_mat.append((last_x,last_y))
        t+=1
    trans_mat = np.array(trans_mat).astype(int)
        
    return trans_mat