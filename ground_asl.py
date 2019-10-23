# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 13:28:32 2019

@author: coeadmin-amoghimi
"""


import cv2
import numpy as np
#import sys
## change this to the folder containing the codes
#code_path = r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master'
#sys.path.append(code_path)
from micasense.reading_metadata import reading_metadata

def ground_asl(band_name, size_obj, FOV):

    img = cv2.imread(band_name)
    _, im_width = img.shape[:-1]
    roi = cv2.selectROI(img)
    n_pixels = roi[2]
    spatial_res = size_obj / n_pixels
    
    agl_alt = spatial_res * im_width / (2*np.tan( (FOV/2)*np.pi/180 ))
    
    meta = reading_metadata(image_folder=None, image_name=None, band_name=band_name)
    flight_alt = meta['Composite:GPSAltitude']
    
    ground_alt = flight_alt - agl_alt
    
    cv2.destroyAllWindows()
    return ground_alt