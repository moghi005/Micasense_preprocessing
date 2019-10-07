# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:38:13 2019

@author: Ali Moghimi
email:	amoghimi@ucdavis.edu


	input:
			path for a folder that contains only images (captured at 5 bands) of the reference panel
            
            'capture_mode' refers to the way images were captured. 
            
                panel_capture_mode = 'manual' -- If the images were captured manually (taking drone by hand), the way Micasense recommend. 
                Panel_capture_mode = 'drone' --  If the images were captured while the drone was flying over the panel. 
                
                
            *** 
            NOTE:
                you may require to play with the thresholds depending on the altitude and other conditions.
            ***
                    
"""



import numpy as np
import cv2
import glob
import skimage
#import micasense.metadata as metadata


# from skimage import morphology

def panel_segmentation(panel_path, panel_capture_mode = 'manual'):
    
    """ segments the panel from the background"""
    
    
    
    # ---------- setting the required thresholds ------------------------------
    
    panel_corners = []
	
    if panel_capture_mode == 'manual':
        area_threshold_min = 15000
        area_threshold_max = 70000
        ratio_threshold = 0.95
        buffer = 3
	
    elif panel_capture_mode == 'drone':
        area_threshold_min = 100
        area_threshold_max = 5000
        ratio_threshold = 0.95
        buffer = 5
        
    elif panel_capture_mode == 'altitude':
        area_threshold_min = 10
        area_threshold_max = 100
        ratio_threshold = 0.95
        buffer = 1
        
    else:
        print('ERROR: panel capture mode should be either "manual" or "drone"')

    
    image_names = [f for f in sorted(glob.glob(panel_path + "**/*.tif", recursive=True))]

    for band in range(len(image_names)):


        # ----------- Reading image ---------------------------------------------------

        img = cv2.imread(image_names[band], -1)  # reading one band at a time
#                cv2.imshow('img', img)
#                cv2.waitKey()
#                cv2.destroyAllWindows()

        # ---------- thresholding - make it binary ------------------------------------

        # Otsu's thresholding after Gaussian filtering
        blur = cv2.GaussianBlur(img, (5, 5), 0)
        _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # ret3,bw = cv2.threshold(blur,0,255,cv2.THRESH_BINARY)
        
#        cv2.imshow('img', bw)
#        cv2.waitKey(0)
#        cv2.destroyAllWindows()

        # ----------- labeling the objects in the binary image  -----------------------

        label_image = skimage.measure.label(bw, connectivity=2)

        # ----------- properties of the objects in the binary image  -----------------------

        props = skimage.measure.regionprops(label_image, intensity_image=None)

        #        axis_ratio = np.zeros((len(props),1))

        reference_panel_mask = np.zeros((bw.shape))

        for j in range(0, len(props)):

            # filtering small objects based on their area
            area_obj = props[j].area
            if area_obj < area_threshold_min or area_obj > area_threshold_max:
                continue

            else:
                MajorAxisLength = props[j].major_axis_length
                MinorAxisLength = props[j].minor_axis_length
                axis_ratio_obj = MinorAxisLength / MajorAxisLength
                # masking objects based on the axis ratio - we know our panel is square
                if axis_ratio_obj >= ratio_threshold:
                    reference_panel_mask[label_image == j + 1] = 255  # plus one because of background (it is zero)

#               cv2.imshow('img', reference_panel_mask)
#               cv2.waitKey(0)
#               cv2.destroyAllWindows()

        temp_im = reference_panel_mask
        n_row, n_col = temp_im.shape

        area_rect = 0

        for i in range(n_row):
            for j in range(n_col):

                if temp_im[i, j] == 0:
                    continue
                else:

                    a = 1
                    # move in rows
                    while temp_im[i + a, j] == 255:
                        a = a + 1
                        #                temp_im[i+a, j] = 0
                        if a == 1:
                            continue
                    a = a - 1
                    b = 1
                    # move in columns
                    while temp_im[i, j + b] == 255:
                        b = b + 1
                        #                temp_im[i, j+b] = 0
                        if b == 1:
                            continue
                    b = b - 1
                    c = 1
                    while temp_im[i + a, j + c] == 255:
                        c = c + 1
                    c = c - 1
                    if c < b:
                        width_rect = c
                    else:
                        width_rect = b

                    temp_area = (a + 1) * (width_rect + 1)

                    if temp_area > area_rect:
                        area_rect = temp_area
                        i_top_left_corner = i
                        j_top_left_corner = j
                        height = a
                        width = width_rect

        img4 = np.repeat(temp_im[:, :, np.newaxis], 3, axis=2)
        
       # if the image was taken from an altitude (not from the ground), then Atso algorithm might detect the margins of the panel
       # to remove those mixed pixels at the margins of the panel, we can do this: 
        if panel_capture_mode == 'drone':
            j_top_left_corner = j_top_left_corner + buffer
            i_top_left_corner = i_top_left_corner + buffer
            width = width - (2*buffer)
            height = height - (2*buffer)
        
        
        top_left_corner = [j_top_left_corner, i_top_left_corner]
        top_right_corner = [j_top_left_corner+width, i_top_left_corner]
        bottom_right_corner = [j_top_left_corner+width, i_top_left_corner+height]
        bottom_left_corner = [j_top_left_corner, i_top_left_corner+height]
        
        
        panel_corners.append([top_left_corner, top_right_corner, bottom_right_corner, bottom_left_corner])

        #       cv2.imshow('img', img4)
        
        # uncomment to see the results as a figure
        cv2.rectangle(img4, (j_top_left_corner, i_top_left_corner),
                      (j_top_left_corner + width, i_top_left_corner + height), (0, 0, 255), 2)
        
        
        #       cv2.waitKey(0)
        #       cv2.destroyAllWindows()

        name_im_to_save = image_names[band].replace('.tif', '_mask.png')
        cv2.imwrite(name_im_to_save, img4)
        
        
    return panel_corners
    
    
    
"""
        another method to filter small objects
"""
#        area_threshold = 15000
#        bw_area_masked = skimage.morphology.remove_small_objects(bw, min_size=area_threshold, connectivity=8)
#        cv2.imshow('img', bw_area_masked)
#        cv2.waitKey(0)
#        cv2.destroyAllWindows()  
        
        
        #-----------  statistics output for each label, including the background label
        
#        nb_components, output, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
#        area_of_objects = stats[1:, -1]; # last column is area, and first row is for background.
#        nb_components = nb_components - 1 # because of background
#        
#        # minimum area of objects we want to keep (number of pixels)

#        bw_area_masked = np.zeros((output.shape))
#        #for every object in the image, you keep it only if it's above area_of_objects
#        for i in range(0, nb_components):
#            if area_of_objects[i] >= area_threshold:
#                bw_area_masked[output == i + 1] = 255 # plus one because of background (it is zero)
#               
#        cv2.imshow('img', bw_area_masked)
#        cv2.waitKey(0)
#        cv2.destroyAllWindows() 
#        


# if we want to decide based on the altitude
        
#meta = metadata.Metadata(image_names[0], exiftool_obj=None)
#meta_data = meta.get_all()
#lat = meta.get_item('Composite:GPSLatitude')
#long = meta.get_item('Composite:GPSLongitude')
#elevation = get_elevation(lat, lon)
#import requests
#import pandas as pd

# script for returning elevation from lat, long, based on open elevation data
# which in turn is based on SRTM


#def get_elevation(lat, long):
#    query = ('https://api.open-elevation.com/api/v1/lookup'
#             f'?locations={lat},{long}')
#    r = requests.get(query).json()  # json object, various ways you can extract value
#    # one approach is to use pandas json functionality:
#    elevation = pd.io.json.json_normalize(r, 'results')['elevation'].values[0]
#    return elevation