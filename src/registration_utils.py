#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  4 18:03:34 2021

@author: yifan
"""


import pandas as pd
import numpy as np
from skimage.external import tifffile


################################################
# Registration related
################################################


def findCroppedDim(tiff_path):
    with tifffile.TiffFile(tiff_path) as tif:
        # read tiff
        im_in = tif.asarray()
        if len(im_in.shape) == 4:
            n_frame, n_zstep, y_dim, x_dim = im_in.shape
        else:
            n_frame, n_zstep, n_channel, y_dim, x_dim = im_in.shape
        top = 0
        bottom = y_dim
        left = 0
        right = x_dim
        if len(im_in.shape) == 4:
            for t in range(n_frame):
                if not np.any(im_in[t][0]): # check if empty frame
                    continue
                # top border
                y = 0
                while im_in[t][0][y][int(x_dim/2)] == 0:
                    y+=1
                if top < y:
                    top = y
                # bottom border
                y = y_dim - 1
                while im_in[t][0][y][int(x_dim/2)] == 0:
                    y-=1
                if bottom > y:
                    bottom = y
                # left border
                x = 0
                while im_in[t][0][int(y_dim/2)][x] == 0:
                    x+=1
                if left < x:
                    left = x
                # right border
                x = x_dim - 1
                while im_in[t][0][int(y_dim/2)][x] == 0:
                    x-=1
                if right > x:
                    right = x
        else:
            for t in range(n_frame):
                if not np.any(im_in[t][0]): # check if empty frame
                    continue
                # top border
                y = 0
                while im_in[t][0][0][y][int(x_dim/2)] == 0:
                    y+=1
                if top < y:
                    top = y
                # bottom border
                y = y_dim - 1
                while im_in[t][0][0][y][int(x_dim/2)] == 0:
                    y-=1
                if bottom > y:
                    bottom = y
                
                # left border
                x = 0
                while im_in[t][0][0][int(y_dim/2)][x] == 0:
                    x+=1
                if left < x:
                    left = x
                # right border
                x = x_dim - 1
                while im_in[t][0][0][int(y_dim/2)][x] == 0:
                    x-=1
                if right > x:
                    right = x
    return top, bottom, left, right

def combine(csv_path,n_csv = 2):
    mat = pd.read_csv(csv_path+"1.csv", index_col=0, header=0)
    mat = mat[['X','Y']]
    mat = roi2mat(mat)
    counter = 2
    while counter<=n_csv:
        nextMat = pd.read_csv(csv_path+str(counter) + ".csv",index_col=0, header=0)
        nextMat = nextMat[['X','Y']]
        nextMat = roi2mat(nextMat)
        mat = combine_roi(mat, nextMat)
        counter+=1
    return mat

def register_movie(root, movie_name,pad=True):
    tiff = root+movie_name+'/'+movie_name+'.tif'
    r_tiff =root+movie_name+'/r_'+movie_name+'.tif'
    csv_path = root+movie_name+'/roi/'
    import os
    (_,_,filenames) = next(os.walk(csv_path))
    n_roi = len(filenames)
    print("Number of ROI found: ", n_roi)
    print("Start registration...")
    register_w_roi(tiff,r_tiff,csv_path,n_roi=n_roi,pad=True)
    print("Registration of {} was successful. Saved in {} .".format(movie_name, r_tiff))
    return
    
def register_w_roi(tiff_path,out_tiff_path, csv_path,n_roi=2,high_res=True,compress=1,pad=True):
    trans_mat = combine(csv_path, n_csv = n_roi)
    metadata = register(tiff_path,trans_mat,out_tiff_path,highres=high_res,compress=compress, pad=pad)
    return metadata

def roi2mat(roi_df):
    x = roi_df.iloc[:,0]
    y = roi_df.iloc[:,1]
    translation =[(0,0)]
    x0 = x[0]
    y0 = y[0]
    i = 1
    while i < len(x) :
        diff_x = int(round((x[i] - x0)))
        diff_y = int(round((y[i] - y0)))
        translation.append((diff_x, diff_y))
        i+=1
    
    return translation

def combine_roi(mat1, mat2):
    last_x, last_y = mat1[-1]
    mat2 = [(a+last_x, b+last_y) for a, b in mat2 ]
    mat2 = mat2[1:]
    mat = mat1 + mat2
    return mat

def translate(im_in,translation,hi_res=True,compression=1,padzeros = True):
    '''
        input:
        im_in: input tiff
        translation: translation matrix
        output:
        im_out: output tiff
        
        tifffile documentation: https://scikit-image.org/docs/0.12.x/api/skimage.external.tifffile.html
        '''
    
    # scalar multiply the translation matrix for high-res
    if hi_res == True:
        translation = np.array(translation) * compression
    translation = np.array(translation).astype(int)
    
    n_channel = 1
    if len(im_in.shape) == 5:
        # multiple channel
        print("Multiple channels detected...")
        n_frame, n_zstep, n_channel, y_dim, x_dim = im_in.shape
    else:
        # single channel
        print("Single channel detected...")
        n_frame, n_zstep, y_dim, x_dim = im_in.shape
    
    if padzeros == False:
        # create empty tiff
        im_out = np.zeros(im_in.shape)
        for t in range(n_frame):
            print("Start processing t = " + str(t))
            trans_x, trans_y = translation[t]
            for z in range(n_zstep):
                if n_channel == 1:
                    for y in range(y_dim):
                        for x in range(x_dim):
                            if (x+trans_x < 0) or (y+trans_y < 0):
                                continue
                            elif (x+trans_x >= x_dim) or (y+trans_y >= y_dim):
                                continue
                            else:
                                im_out[t][z][y][x] = im_in[t][z][y+trans_y][x+trans_x]
                else:
                    for ch in range(n_channel):
                        for y in range(y_dim):
                            for x in range(x_dim):
                                if (x+trans_x < 0) or (y+trans_y < 0):
                                    continue
                                elif (x+trans_x >= x_dim) or (y+trans_y >= y_dim):
                                    continue
                                else:
                                    im_out[t][z][ch][y][x] = im_in[t][z][ch][y+trans_y][x+trans_x]

    
    else:
        # search for extrema
        x_low, x_high  = 0, x_dim
        y_low, y_high  = 0, y_dim
        for t in range(n_frame):
            trans_x, trans_y = translation[t]
            if -trans_y < y_low:
                y_low = -trans_y
            if y_dim-trans_y > y_high:
                y_high = y_dim-trans_y
            if -trans_x < x_low:
                x_low = -trans_x
            if x_dim-trans_x > x_high:
                x_high = x_dim-trans_x
            
            x_high, x_low, y_high, y_low = int(x_high), int(x_low), int(y_high), int(y_low)
            x_dim_adj, y_dim_adj = x_high-x_low, y_high-y_low
            #create empty tiff
        if n_channel == 1:
            im_out = np.zeros((n_frame, n_zstep, y_dim_adj, x_dim_adj))
        else:
            im_out = np.zeros((n_frame, n_zstep, n_channel, y_dim_adj, x_dim_adj))
        # translate
        for t in range(n_frame):
            print("Start processing t = " + str(t))
            trans_x, trans_y = translation[t]
            for z in range(n_zstep):
                if n_channel==1:
                    for y in range(y_dim):
                        for x in range(x_dim):
                            im_out[t][z][y-trans_y-y_low][x-trans_x-x_low] = int(im_in[t][z][y][x])
                else:
                    for ch in range(n_channel):
                        for y in range(y_dim):
                            for x in range(x_dim):
                                im_out[t][z][ch][y-trans_y-y_low][x-trans_x-x_low] = int(im_in[t][z][ch][y][x])

    return im_out

def register(tiff_path, trans_mat, out_tiff_path, highres = True, compress = 1, pad = True):
    '''
        tiff_path: tiff file name
        trans_mat: translation matrix, can be obtained by roi2mat()
        highres: optional, if set to True, will multiply the trans_mat by compress (which is set to 3 by default)
        compress: as above
        pad: whehther or not pad the periphery to zeros. If false, will crop the tiff
        
        This function returns a dict of metadata, and writes the tiff to current working directory
        
        '''
    with tifffile.TiffFile(tiff_path) as tif:
        # read tiff
        im_in = tif.asarray()
        # read metadata as tif_tags (dict)
        tif_tags = tif.pages[0].tags.values()
    
    
    # register using trans_mat
    im_out = translate(im_in,trans_mat,hi_res=highres,compression=compress,padzeros=pad)
    im_out = im_out.astype('uint16')
    
    # save registered tiff, no compression
    with tifffile.TiffWriter(out_tiff_path, bigtiff = highres) as tif:
        for i in range(im_out.shape[0]):
            tif.save(im_out[i])
    return tif_tags
