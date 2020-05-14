#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 19:29:46 2020
@filename: track_pairer
@author: yifan
"""
import pandas as pd
from scipy.spatial import distance
from statistics import mean, stdev
import matplotlib.pyplot as plt
from utils.xmlParser import parseTracks, parseSpots
from utils.register import findCroppedDim
from utils.TransMatGenerator import spot,findConv

################################################
# Some helper functions
################################################
def normalize(vector):
    # unpack
    x, y, z = vector
    # calculate length
    length = (x**2 + y**2 + z**2)**0.5
    # divide by length
    if length == 0:
        return (0,0,0)
    return (x/length, y/length, z/length)


def findCong(time, dist, max_dist):
    """
    Counts the number of continuous time points in which the two 
        tracks are under max_dist microns away
    - the time argument is a list of time points in which the two tracks are both present
    
    - the dist argument is the list of corresponding distances
    
    - the max_dist argument is a distance threshold (float or int)
    """
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
        
################################################
# Cell object
################################################
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
        self.dist2border = None # dist from the center of cell to closest tiff border
        self.diam = None
        self.intensity = None
        self.contrast = None
        
################################################
# Edge object
################################################
class edge(object):
    def __init__(self):
        self.source = None
        self.target = None
        self.track_id = None
        self.t = None
        
################################################
# Track object
################################################
class track(object):
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.id = None
        self.t_i = None
        self.t_f = None
        self.duration = None
        self.contrast = None
        self.intensity = None
        self.diameter = None

################################################
# Pairer object
################################################
class TrackPairer(object):
    def __init__(self,xml,conversion,DIM = None,maxdist=11,mindist=4,maxcongdist=4,minoverlap=10):
        """
        Initialzing a pairer object
        
        - The xml argument is path of the TrackMate xml input, as a string
        
        - The conversion argument is a dictionary of pixel to micon conversion for x, y, z
        
        - The DIM argument is an option for user to input the dimension (width,y=height) of the movie, optional
        
        - The maxdist argument is a distance threshold of how far away two paired centrosomes can be at any time point
        
        - The maxcongdist argument is a distance threshold of hor far away two centrosomes can be but still counted as "in congression"
        
        - The minoverlap argument is a duration threshold. Two tracks with fewer overlapped frames will be filtered.
    
        - The mindist arguent is a distance threshold of the minimum proximity two centrosomes must have for at least 1 time frame in order to be considered as "paired"
        """
        # store the provided variables
        self.xml_path = xml
        self.min_overlap = minoverlap
        self.max_dist = maxdist/conversion['x']
        self.min_dist = mindist/conversion['x']
        self.maxcongdist = maxcongdist/conversion['x']
        self.DIM = DIM
        
        # create dynamic variables
        self.nbrTracks = []
        self.allTracks = {}
        self.allSpots = {}
        self.allEdges = {}
        self.cells = []
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None
        
    def track_dist2border(self, x, y):
        '''
        Finds the distance of track mean position to the closest border
        '''
        toTop = y - self.top
        toBottom = self.bottom - y 
        toLeft = x - self.left
        toRight = self.right - x
        return min([toTop, toBottom, toLeft, toRight])

        
    def getAllTracks(self, f, originalMovie):
        # read tiff dim
        if self.DIM == None:
            self.top, self.bottom, self.left, self.right = findCroppedDim(tiff_path = originalMovie)
        # read from xml all info about tracks
        track_general, track_detail = parseTracks(self.xml_path)
        # populate edge objects
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
            myTrack.diameter, myTrack.contrast, myTrack.intensity = self.findTrackInfo(myTrack)
            # apply the border filter
            dist2border = self.track_dist2border(myTrack.x, myTrack.y)
            if dist2border <= 0: # track on border, discard the track
                f.write(str(int(myTrack.id)) + ' not included: outside border\n')
                continue
            # apply the track duration filter
            if myTrack.duration < self.min_overlap:
                f.write(str(int(myTrack.id)) +' not included: duration less than min_overlap\n')
                continue
            # centrosome diameter filter
            self.allTracks[myTrack.id] = myTrack
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
            mySpot.diam = float(row['ESTIMATED_DIAMETER'])
            mySpot.maxInt = float(row['MAX_INTENSITY'])
            mySpot.contrast = float(row['CONTRAST'])
            self.allSpots[mySpot.id] = mySpot
        return self.allSpots
    
    def findTrackInfo(self, myTrack):
        t = myTrack.t_i
        maxInt = []
        diam = []
        contrast = []
        while t <= myTrack.t_f:
            if t not in self.allEdges[myTrack.id]: 
                t+=1
                continue
            spotID = self.allEdges[myTrack.id][int(t)]
            spot = self.allSpots[spotID]
            maxInt.append(spot.maxInt)
            contrast.append(spot.contrast)
            diam.append(spot.diam)
            t+=1
        return mean(diam), mean(contrast), mean(maxInt)
        
    
    def findDist(self, id_i, id_j):
        '''
        finds the distance between two tracks over time
        input: id_i and id_j are track id's
        '''
        # create list of time
        time = [] 
        # create a list of corresponding distance 
        sl = []
        centers = {'x': [], 'y':[], 'z': []}
        normals = {'x': [], 'y':[], 'z': []}
        # get track objects by id
        trackI = self.allTracks[id_i]
        trackJ = self.allTracks[id_j]
        # find start and stop time (overlapped between two tracks)
        start = max([trackI.t_i,trackJ.t_i])
        stop = min([trackI.t_f, trackJ.t_f])
        if stop - start <= 0:
            return
        t = start 
        
        while t < stop :    
            # calculate distance
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
            # update dynamic variables
            time.append(t)
            sl.append(dist)
            centers['x'].append(center[0])
            centers['y'].append(center[1])
            centers['z'].append(center[2])
            normals['x'].append(n_normal[0])
            normals['y'].append(n_normal[1])
            normals['z'].append(n_normal[2])
            t+=1
        return sl, centers, normals, time
          
    def cell_dist2border(self):
        '''
        Finds the distance of cell center to the closest border
        '''
        for myCell in self.cells:          
            # unpack cell_center
            x, y, z = myCell.center
            toTop = y - self.top
            toBottom = self.bottom - y 
            toLeft = x - self.left
            toRight = self.right - x
            myCell.dist2border = min([toTop, toBottom, toLeft, toRight])

    def findNeighbors(self, f, originalMovie):
        # 1. spots bookkeeping
        self.allSpots = self.getAllSpots()
        # 2. tracks and edges bookkeeping
        self.allTracks = self.getAllTracks(f, originalMovie)
        # 3. find neighbors by crude filters
        print("Total number of tracks: " + str(len(self.allTracks)) )
        for myTrack in self.allTracks.values():            
            for nbr in self.allTracks.values():
                # 1) if track duration less than min_overlap, out
                if nbr.duration < self.min_overlap:
                    continue
                # 2)  myTrack is the same track as nbr, out
                elif myTrack.id == nbr.id:
                    continue
                # 3) find period of overlap: if fewer frames than min_overlap , out
                t_start = max([myTrack.t_i, nbr.t_i])
                t_stop = min([myTrack.t_f, nbr.t_f])
                if t_stop - t_start < self.min_overlap:
                    f.write(str(int(myTrack.id)) + ' and ' + str(int(nbr.id)) + ' not pair: overlap time too short\n')
                    continue
                # 4) find max distance: if greater than max_dist um, out
                dist, centers, normals, time = self.findDist(myTrack.id, nbr.id)
                avg_dist = mean(dist)
                max_dist = max(dist)
                min_dist = min(dist)
                if avg_dist > self.max_dist:
                    f.write(str(int(myTrack.id)) + ' and ' + str(int(nbr.id)) + ' not pair: too far away\n')
                    continue
                # 5) find min distance, if greater than min_dist microns, out FOR DEBUG
                if min_dist > self.min_dist:
                    f.write(str(int(myTrack.id)) + ' and ' + str(int(nbr.id)) + ' not pair: too far away (min distance filter) \n')
                    continue
                # filtering finished, fill in cell info
                myCell = cell()
                myCell.centID_i = myTrack.id
                myCell.centID_j = nbr.id
                myCell.t_overlap = t_stop - t_start
                myCell.sl_i = dist[0]
                myCell.sl_f = dist[-1]
                myCell.sl_max = max_dist
                myCell.sl_min = min_dist
                myCell.center = (mean(centers['x']), mean(centers['y']), mean(centers['z']))
                stdev_x = stdev(centers['x'])
                stdev_y = stdev(centers['y'])
                stdev_z = stdev(centers['z'])
                stdev_x_n = stdev(normals['x'])
                stdev_y_n = stdev(normals['y'])
                stdev_z_n = stdev(normals['z'])
                myCell.center_stdev = (stdev_x**2 + stdev_y**2 + stdev_z**2)**0.5
                myCell.normal_stdev = (stdev_x_n**2 + stdev_y_n**2 + stdev_z_n**2)**0.5
                myCell.t_cong = findCong(time, dist, self.maxcongdist)
                myCell.contrast = (myTrack.contrast + nbr.contrast)/2
                myCell.intensity = (myTrack.intensity + nbr.intensity)/2
                myCell.diameter = (myTrack.diameter + nbr.diameter)/2
                self.cells.append(myCell)
        self.cell_dist2border()
        return self.cells
    
    def linkID(self, trackIDList):
        '''
        Creates a dictionary of trackID: [SpotIDs]
        '''
        track2spot = {}
        spot2track = {}
        for trackID in trackIDList:
            track2spot[trackID] = []
            track = self.allTracks[trackID]
            start = track.t_i
            stop = track.t_f            
            t = start 
            while t < stop :    
                if t not in self.allEdges[trackID]: 
                    t+=1
                    continue
                # get spot id
                spotID = self.allEdges[trackID][t]
                t+=1
                track2spot[trackID].append(spotID)
                spot2track[spotID] = trackID
        return track2spot, spot2track
        
    def pred2SpotCSV(self,conversion,r_xml_path,out_folder,out_name,framerate=1):
        pred = pd.read_csv(out_folder+'/.temp/predictions.csv')
        spots = parseSpots(r_xml_path)
        allTracks = []
        allPairs = []
        for index, row in pred.iterrows():
            if int(row['Predicted_Label']) == 1 :
                i = int(row['centID_i'])
                j = int(row['centID_j'])
                allTracks.append(i)
                allTracks.append(j)
                allPairs.append((i,j))
        allTracks = list(set(allTracks)) # unique
        track2spots, spot2track = self.linkID(allTracks) # link spot to track
        for i, j in allPairs:
            if (j,i) in allPairs:
                allPairs.remove((j,i))
                
        allSpotIDs = []        
        for k, v in track2spots.items():
            allSpotIDs = allSpotIDs + v
        mySpots = {}    
        for index, row in spots.iterrows():
            spotID = int(row['ID'])
            if spotID in allSpotIDs:
                row['TRACK_ID'] = spot2track[spotID]
                mySpots[spotID]=row
        counter = 0
        allSpots = []
        for i, j in allPairs:
            counter+=1
            spots_i = track2spots[i]
            spots_j = track2spots[j]
            name_i ='Cent_'+str(counter)+'a'
            name_j ='Cent_'+str(counter)+'b'
            for spotID in spots_i:
                spotSeries = mySpots[spotID].copy()
                spotSeries['Label'] = name_i
                allSpots.append(spotSeries)
            for spotID in spots_j:
                spotSeries = mySpots[spotID].copy()
                spotSeries['Label'] = name_j
                allSpots.append(spotSeries)
        df = pd.DataFrame(allSpots)
        # reorder
        df = df[["Label", "ID", "TRACK_ID",
                 "QUALITY", "POSITION_X","POSITION_Y", 
                 "POSITION_Z", "POSITION_T", "FRAME", 
                 "RADIUS", "VISIBILITY", "MANUAL_COLOR", 
                 "MEAN_INTENSITY", "MEDIAN_INTENSITY",
                 "MIN_INTENSITY", "MAX_INTENSITY",
                 "TOTAL_INTENSITY", "STANDARD_DEVIATION",
                 "ESTIMATED_DIAMETER", "ESTIMATED_DIAMETER", "SNR"]]
        
        df['POSITION_Z'] = df['POSITION_Z'].astype('float') * conversion['z']
        df['POSITION_X'] = df['POSITION_X'].astype('float') * conversion['x']
        df['POSITION_Y'] = df['POSITION_Y'].astype('float') * conversion['y']
        df['POSITION_T'] = df['POSITION_T'].astype('float') * framerate 
        
        df.to_csv(out_name, index=False)
        print("Number of cells found: " + str(len(allPairs)))
        return allSpots, allPairs

def cell2df(cells):
    myDict = {'center_stdev': [],
              'normal_stdev': [],
              'sl_f': [],
              'sl_i': [],
              'sl_max': [],
              'sl_min': [],
              't_cong': [],
              't_overlap': [],
              'intensity': [],
              'diameter': [],
              'contrast': [],
              'centID_i': [],
              'centID_j': []}
    for myCell in cells:
        myDict['center_stdev'].append(myCell.center_stdev)
        myDict['normal_stdev'].append(myCell.normal_stdev)
        myDict['sl_f'].append(myCell.sl_f)
        myDict['sl_i'].append(myCell.sl_i)
        myDict['sl_max'].append(myCell.sl_max)
        myDict['sl_min'].append(myCell.sl_min)
        myDict['t_cong'].append(myCell.t_cong)
        myDict['t_overlap'].append(myCell.t_overlap)
        myDict['intensity'].append(myCell.intensity)
        myDict['diameter'].append(myCell.diameter)
        myDict['contrast'].append(myCell.contrast)
        myDict['centID_i'].append(myCell.centID_i)
        myDict['centID_j'].append(myCell.centID_j)
    df = pd.DataFrame(myDict)
    return df

def pair(clf,r_xml_path,originalMovie,out_folder,final_out,framerate=1,maxdist=11,mindist=4,maxcongdist=4,minoverlap=10,dim=None):
    f = open(out_folder+'.temp/console.txt', 'w')
    print('Pairing tracks in the movie: ' + originalMovie)
    c = findConv(originalMovie)
    # crude pairer, generate features
    if dim == None:
        myPairer = TrackPairer(r_xml_path,c,maxdist=maxdist,mindist=mindist,maxcongdist=maxcongdist,minoverlap=minoverlap)
    else: 
        myPairer = TrackPairer(r_xml_path,c,DIM = dim,maxdist=maxdist,mindist=mindist,maxcongdist=maxcongdist,minoverlap=minoverlap)
        myPairer.left, myPairer.right, myPairer.top, myPairer.bottom = dim 
    
    cells = myPairer.findNeighbors(f, originalMovie)
    df = cell2df(cells)
    df.to_csv (out_folder+'/.temp/features.csv', index = False, header=True)
    print("Potential pairs generated.")
    # generate features panel for ml clf
    X_df = pd.read_csv(out_folder+'/.temp/features.csv', usecols = range(11))
    X = X_df.to_numpy()
    # load the model from disk
    # predict
    y_pred = clf.predict(X)
    df['Predicted_Label'] = y_pred
    df.to_csv (out_folder+'/.temp/predictions.csv', index = False, header=True)
    print("Predictions generated.")
    f.close()
    myPairer.pred2SpotCSV(c,r_xml_path,out_folder,final_out,framerate=framerate)
        