# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 16:43:25 2020

@author: Ali Moghimi
email: amoghimi@ucdavis.edu

"""
import sys
# change this to the folder containing the codes
code_path = r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master'
sys.path.append(code_path)

import micasense.imageset as imageset
import micasense.capture as capture
import pandas as pd
import numpy as np
import os
import cv2
import micasense.irradiance_correction_by_panel as compute_irr
import micasense.imageutils as imageutils
import rasterio as rio
from micasense.save_metadata import saveMetadata

reference_panel = 'micasense'  # 'tarp_26'  or 'micasense'

image_path = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\RedEdge Camera and DLS Experiments\Radiometric calibration tests\Data\20-2-4 - Experiment 3 - Two Tarps\tarp_images'

if reference_panel == 'micasense':
    panel_path = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\RedEdge Camera and DLS Experiments\Radiometric calibration tests\Data\20-2-4 - Experiment 3 - Two Tarps\panel_before\panel_before'
    path_to_save = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\RedEdge Camera and DLS Experiments\Radiometric calibration tests\Data\20-2-4 - Experiment 3 - Two Tarps\Reflectance\panel'

if reference_panel == 'tarp_26':
    panel_path = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\RedEdge Camera and DLS Experiments\Radiometric calibration tests\Data\20-2-4 - Experiment 3 - Two Tarps\Reflectance\tarp_26\tarp_before'
    path_to_save = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\RedEdge Camera and DLS Experiments\Radiometric calibration tests\Data\20-2-4 - Experiment 3 - Two Tarps\Reflectance\tarp_26'
    

flight_alt = 10
panel_detection_mode = 'default'
warp_mode = cv2.MOTION_HOMOGRAPHY

# In[]
''' ====================== compute IRRADIANCE by panel ======================  '''

panel = compute_irr.Irradiance_correction_by_panel(panel_path, reference_panel = reference_panel, panel_detection_mode = panel_detection_mode, panel_capture_mode = 'manual')
panel_reflectance_by_band = panel.panel_actual_reflectance_by_band
print(panel_reflectance_by_band)
#cor = panel.panel_corners
#panel.plot_panel_location()
#panel.coef_in_situ()
#panel.plot_redi_irradi()
#panel.plot_panel_reflectance()

dn_panel = []
for band in range(0,5):
    
    dn = panel.cap.images[band].raw()
    if panel_detection_mode == 'default' and reference_panel == 'micasense':
         bottom_r, _, top_l, _ = panel.panel_corners[band]
    elif panel_detection_mode == 'my_func' or reference_panel != 'micasense':
         top_l, _, bottom_r, _ = panel.panel_corners[band]
    # top_left_corner = [j_top_left_corner, i_top_left_corner] so it is in image coordinates not matrix cooridinate
    panel_cropped = dn[top_l[1]:bottom_r[1], top_l[0]:bottom_r[0]]
    dn_panel.append(np.mean(panel_cropped, (0,1)))
    
irradiance = (np.pi * np.array(dn_panel)) / panel_reflectance_by_band

# In[] 
''' ======================== Alignment matrix ===========================  '''
import pickle
alignment_mat_path = r'G:\My Drive\Davis\Research\Python\MicaSense\Alignment Matrix\\alignment_micasense_10_120_m.pkl'
pickle_in = open(alignment_mat_path,"rb")
alignment_micasense = pickle.load(pickle_in)
alt_align_mat_measured = [key for key in alignment_micasense.keys() if isinstance(key, (int, float, complex))]

delta_alt = abs(np.array(alt_align_mat_measured) - flight_alt)
if np.min(delta_alt) < 5:
    ind = int(np.where(delta_alt==np.min(delta_alt))[0])
    alt_align_close_to_flight_alt = alt_align_mat_measured[ind]
    warp_matrices = [alignment_micasense[alt_align_close_to_flight_alt][band] for band in alignment_micasense[alt_align_close_to_flight_alt]]
else:
    raise IOError('Error: could not find a proper alignment matrix for this altitue!')
            
            
# In[]      
''' ================= convert to REFLECTANCE and STACK together=================  '''
        
imlist = imageset.ImageSet.from_directory(image_path)

# -------------- convert the imagelist to Panda data frame --------------------
data, columns = imlist.as_nested_lists()
df = pd.DataFrame.from_records(data, index='capture_id', columns=columns)

for cap in imlist.captures:
    
    cropped_dimensions,_ = imageutils.find_crop_bounds(cap,warp_matrices,warp_mode=warp_mode)
  
    stacked_reflectance = imageutils.my_alignment(cap, warp_matrices, warp_mode, cropped_dimensions, irradiance, interpolation_mode=cv2.INTER_LANCZOS4)
    panel_cropped_bands = stacked_reflectance[top_l[1]:bottom_r[1], top_l[0]:bottom_r[0], :]    
    np.mean(panel_cropped_bands, (0,1))    
    
    
    '''save the stacked'''
    image_name_blue = cap.images[0].meta.get_item("File:FileName")
    image_name = image_name_blue[0:-6] # remove '_1.tif'
    outputFilename = image_name+'.tif'
        
    outputPath_for_stacked = os.path.join(path_to_save, outputFilename)
    with rio.open(outputPath_for_stacked,
                   'w', 
                   driver='GTiff', 
                   height=stacked_reflectance.shape[0], 
                   width=stacked_reflectance.shape[1],
                   count=stacked_reflectance.shape[2],
                   dtype=stacked_reflectance.dtype) as dst:
    
        for band in range(stacked_reflectance.shape[2]):
            dst.write(stacked_reflectance[:,:,band], (band+1))
        dst.close()            

    # save Metadata
    save_meta = saveMetadata(cap, path_to_save)
    save_meta.save_metadata_pix4D(path_to_save, mode = 'stack')
    save_meta.save_metadata_envi()
