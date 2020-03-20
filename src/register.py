#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 14:39:54 2020
@filename: register.py
@author: Yifan Zhao
@description: Register a tiff file using user-provided ROI
"""
import pandas as pd
import os
import numpy
from skimage.external import tifffile


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
    mat2 =  [(a+last_x, b+last_y) for a, b in mat2 ]
    mat = mat1 + mat2
    return mat
    

def translate(im_in, translation, hi_res = False, compression = 3, padzeros = True):
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
        translation = numpy.array(translation) * compression
    
    translation = numpy.array(translation).astype(int)
    n_frame, n_zstep, y_dim, x_dim = im_in.shape
        
    if padzeros == False:       
        # create empty tiff
        im_out = numpy.zeros(im_in.shape)                    
        for t in range(n_frame): 
            if t%20 == 0:
                print("Start processing t = " + str(t))
            trans_x, trans_y = translation[t]
            for z in range(n_zstep):
                for y in range(y_dim):
                    for x in range(x_dim):
                        if (x+trans_x < 0) or (y+trans_y < 0):
                            continue
                        elif (x+trans_x >= x_dim) or (y+trans_y >= y_dim):
                            continue
                        else:
                            im_out[t][z][y][x] = im_in[t][z][y+trans_y][x+trans_x]
    else:            
        # search for extrema
        x_low, x_high  = 0, x_dim
        y_low, y_high  = 0, y_dim
        for t in range(n_frame): 
            trans_x, trans_y = translation[t]
            if trans_y < y_low:
                y_low = trans_y
            if y_dim+trans_y > y_high:
                    y_high = y_dim+trans_y
            if trans_x < x_low:
                x_low = trans_x
            if x_dim+trans_x > x_high:
                    x_high = x_dim+trans_x
        

        x_high, x_low, y_high, y_low = int(x_high), int(x_low), int(y_high), int(y_low)
        x_dim_adj, y_dim_adj = x_high-2*x_low, y_high - 2*y_low
#        x_diff, y_diff = x_dim_adj-x_dim, y_dim_adj-y_dim #-1 for indexing
        #create empty tiff
        im_out = numpy.zeros((n_frame, n_zstep, y_dim_adj, x_dim_adj))
        # translate
        for t in range(n_frame):
            if t%20 == 0:
                print("Start processing t = " + str(t))
#             if t>10: break
            trans_x, trans_y = translation[t]
            for z in range(n_zstep):
                for y in range(y_dim):
                    for x in range(x_dim):
                        im_out[t][z][y-trans_y-y_low][x-trans_x-x_low] = int(im_in[t][z][y][x])
                        
    return im_out




def register(tiff_path, trans_mat, highres = False, compress = 3, pad = True):
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
    im_out = translate(im_in, trans_mat, hi_res = highres, compression = compress, padzeros = pad)
    im_out = im_out.astype('uint16')
    
    # save registered tiff, no compression
    with tifffile.TiffWriter("r_" + tiff_path, bigtiff = highres) as tif:
        for i in range(im_out.shape[0]):
            tif.save(im_out[i])
    return tif_tags


if __name__ == "__main__":
    
    # example usage
    os.chdir("../data/2018-01-16_GSC_L4_L4440_RNAi/")

    # --- step 1: get transformation matrix (2D) ---
    mat1 = pd.read_csv("1.csv", header = None)
    mat1 = roi2mat(mat1)
    mat2 = pd.read_csv("2.csv", header = None)
    mat2 = roi2mat(mat2)
    trans_mat = combine_roi(mat1, mat2)
    
#    # --- step 2: get ground truth tiff (low res) ---
#    tiff_path = 'low_res.tif'
#    metadata = register(tiff_path, trans_mat)
    
    # --- step 3: get ground truth tiff (high res) ---
    tiff_path = 'u_germline.tif'
    metadata = register(tiff_path, trans_mat, highres = True, compress = 3)
    
    
