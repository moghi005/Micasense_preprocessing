# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 17:10:33 2019

@author: coeadmin-amoghimi
"""

import sys
# change this to the folder containing the codes
sys.path.append(r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master')

from micasense.Micasense_pre_processing_wrapper import pre_processing





panel_path_before = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\Vineyard Matt\2019\Selma\19-7-18 - Vineyard Matt- Selma - Harvest\Images\MS\Demo\paenl\panel_before'
panel_path_after = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\Vineyard Matt\2019\Selma\19-7-18 - Vineyard Matt- Selma - Harvest\Images\MS\Demo\paenl\panel_after'
image_path = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\Vineyard Matt\2019\Selma\19-7-18 - Vineyard Matt- Selma - Harvest\Images\MS\Demo\images'
flight_alt = 70 # altitude (in meter) above the ground 


alignment_mat_path = r'G:\My Drive\Davis\Research\Python\MicaSense\Alignment Matrix\\alignment_micasense_attempt_4_green_pyramid0.pkl'
    
    
#pre_processing(image_path, panel_path_before, panel_path_after, alignment_mat_path, flight_alt)

pre_processing(image_path,
                   panel_path_before,
                   panel_path_after,
                   alignment_mat_path,
                   flight_alt,
                   panel_detection_mode = 'my_func',
                   panel_capture_mode = 'manual',
                   save_as_geotiff = False,
                   generateThumbnails = True,
                   generateIndividualBands = False,
                   overwrite = True,
                   envi_metadata = True,
                   pix4D_metadata = True)