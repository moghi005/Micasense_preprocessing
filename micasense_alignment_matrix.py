# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 10:30:42 2019

@author: coeadmin-amoghimi
Ali Moghimi
amoghimi@ucdavis.edu


ground_level = None, images that captured while the UAV was on the ground to record the altitude of the ground above the sea level
                     otherwise, user should enter the ASL altitude.

Alignment settings:
    match_index = 1 # Index of the band 
    max_alignment_iterations = 50
    warp_mode = cv2.MOTION_HOMOGRAPHY # MOTION_HOMOGRAPHY or MOTION_AFFINE. For Altum images only use HOMOGRAPHY
    pyramid_levels_1 = None # for images with RigRelatives, setting this to 0 or 1 may improve alignment
    pyramid_levels_1 = 0 # for images with RigRelatives, setting this to 0 or 1 may improve alignment
    
    
    
"""

import sys
sys.path.append(r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master')
import micasense.imageset as imageset
import numpy as np
import pandas as pd
import cv2
import micasense.imageutils as imageutils


def micasense_alignment_matrix(image_path,
                               ground_level = None,
                               max_alignment_iterations = 50,
                               match_index = 1, # Index of the band
                               warp_mode = cv2.MOTION_HOMOGRAPHY,
                               pyramid_levels_1 = 0):

    imset = imageset.ImageSet.from_directory(image_path)
    
    data, columns = imset.as_nested_lists()
    df = pd.DataFrame.from_records(data, index='timestamp', columns=columns)
    
    #lat = np.array(df.iloc[0]['latitude'])
    #lon = np.array(df.iloc[0]['longitude'])
    alt_asl = np.array(df.iloc[:]['altitude'])
    
    if ground_level == None:
        ground_level = np.min(alt_asl)
    # or enter manually
    #ground_level = 106.48 # altitude above sea level 
    
    alt_agl = alt_asl - ground_level
    df['altitude'] = alt_agl
    
    a_increment = 0
    alignment_matrix = {}
    wrap_matrix = {}
    alignment_matrix["altitude"] = np.round(alt_agl)
    
    
    for cap in imset.captures:
        
        if cap.location()[2] == ground_level:
            continue # if the this is the imageset captured on the ground, then continue
        

        
        # Can potentially increase max_iterations for better results, but longer runtimes
        warp_matrices, alignment_pairs = imageutils.align_capture(cap,
                                                                  ref_index = match_index,
                                                                  max_iterations = max_alignment_iterations,
                                                                  warp_mode = warp_mode,
                                                                  pyramid_levels = pyramid_levels_1,
                                                                  multithreaded=True)
#        if
#        TypeError: findTransformECC() missing required argument 'inputMask' (pos 6)
#        run the following
#        
#        (cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria, None, 1)
    

        
    #    print("Finished Aligning, warp matrices={}".format(warp_matrices))
        wrap_matrix["Blue"] = warp_matrices[0]
        wrap_matrix["Green"] = warp_matrices[1]
        wrap_matrix["Red"] = warp_matrices[2]
        wrap_matrix["NIR"] = warp_matrices[3]
        wrap_matrix["RedEdge"] = warp_matrices[4]
    
        alt = int(cap.location()[2] - ground_level)
        alignment_matrix[alt] = wrap_matrix
        a_increment += 1
        print("iteration {} out of {}".format(a_increment, len(df)))
        
        print("Finished Aligning, warp matrices={}".format(warp_matrices))        
    
        wrap_matrix = {}
           
    alignment_param = alignment_pairs[0].copy() # it is the same for all the bands and all altitudes, so save one of them
    alignment_param.pop("ref_image")            # ref_image is different for each image and band, so remove it 
    alignment_matrix["alignment_param"] = alignment_param
    
    return alignment_matrix

