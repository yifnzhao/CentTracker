#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  4 18:04:28 2021

@author: yifan
"""

import pandas as pd
import numpy as np
import xml.etree.cElementTree as et

################################################
# XML parsing related
################################################

def parseSpots(trackmate_xml_path):
    '''
    trackmate_xml_path : str
    parses the spots info from trackmate xml
    code adaptd from: https://github.com/hadim/pytrackmate
    '''
    root = et.fromstring(open(trackmate_xml_path).read())
    objects = []
    features = root.find('Model').find('FeatureDeclarations').find('SpotFeatures')
    features = [c.get('feature') for c in features.getchildren()] + ['ID'] + ['name']

    spots = root.find('Model').find('AllSpots')
    objects = []
    for frame in spots.findall('SpotsInFrame'):
        for spot in frame.findall('Spot'):
            single_object = []
            for label in features:
                single_object.append(spot.get(label))
            objects.append(single_object)

    spots_df = pd.DataFrame(objects, columns=features)

    return spots_df


def parseTracks(trackmate_xml_path):
    '''
    trackmate_xml_path : str
    
    this function complements pytrackmate module by parsing the tracks info 
        from trackmate xml file
        
    returns:
        df: a pandas dataframe containing general information per track, 
        df2: a pandas dataframe containing specific info per edge

    reference: 
        https://imagej.net/TrackMate
    '''
    
    tree = et.parse(trackmate_xml_path)
    root = tree.getroot()
    objects = []
    df = pd.DataFrame([])
    df2 = pd.DataFrame([])
    features = root.find('Model').find('FeatureDeclarations').find('TrackFeatures')
    features = [c.get('feature') for c in features.getchildren()]
    features.append('name')
    tracks = root.find('Model').find('AllTracks')
    objects = []
    edges = []
    
    for track in tracks.findall('Track'):
        single_object = []
        track_id = int(track.get("TRACK_ID"))
        for edge in track.findall('Edge'):
            edge_object = [track_id,
                    edge.get('SPOT_SOURCE_ID'), 
                     edge.get('SPOT_TARGET_ID'), 
                     edge.get('LINK_COST'),
                     edge.get('EDGE_TIME'),
                     edge.get('EDGE_X_LOCATION'),
                     edge.get('EDGE_Y_LOCATION'),
                     edge.get('EDGE_Z_LOCATION'),
                     edge.get('VELOCITY'),
                     edge.get('DISPLACEMENT')]
            
            edges.append(edge_object)               
        
        for label in features:
            single_object.append(track.get(label))
        objects.append(single_object)
      
        
    df = pd.DataFrame(objects, columns = features)
    #df = df.astype(np.float)
    df2 = pd.DataFrame(edges, columns = [
                    'TRACK_ID',
                    'SPOT_SOURCE_ID',
                    'SPOT_TARGET_ID',
                    'LINK_COST',
                    'EDGE_TIME',
                    'EDGE_X_LOCATION',
                    'EDGE_Y_LOCATION',
                    'EDGE_Z_LOCATION',
                    'VELOCITY',
                    'DISPLACEMENT'])
    df2 = df2.astype(np.float)
    
    return df, df2

def parseDim(trackmate_xml_path):
    f=open(trackmate_xml_path)
    ln=f.readline().split()
    while ln[0] != 'Geometry:':
        ln=f.readline().split()
    ln=f.readline().split()
    X = int(ln[4][:-1])
    ln=f.readline().split()
    Y = int(ln[4][:-1])
    ln=f.readline().split()
    Z = int(ln[4][:-1])
    ln=f.readline().split()
    T = int(ln[4][:-1]) 
    f.close()
    return (X,Y,Z,T)

