# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 17:10:33 2019

@author: Ali Moghimi
Email: amoghimi@ucdavis.edu
-------------------------------------------------------------------------------

    image_path: Folder path for the images. It can contain several sub folders. 
    
    panel_path_before: it contains the images of the panel captured BEFORE the flight. Only one set of image (5 bands) should be in this folder. 
                       if you don't provide the path for panels, it will only use DLS data to convert the radiance to reflectance. 
    
    panel_path_after: it contains the images of the panel captured AFTER the flight. Only one set of image (5 bands) should be in this folder. This is just
                      to check if we get the expected reflectance values from the panel after all of the preprocessing steps. 
    
    alignment_mat_path: Folder path for the alignment matrices calculated for various altitudes. 
    
    flight_alt: the above ground altitude (in meter) at which the UAV flew. 
    
    ground_alt: define the altitude of the ground above the sea level - the algorithm subtract the altitude read my GPS from teh ground alt to calculate the flight alt
                use this only if you flew manually and it was hard for the pilot to keep the flight alt consistent. 
    
    panel_detection_mode: There are two options:
                •	‘default’ which is the Micasense algorithm for panel detection using the QR code. 
                •	‘my_func’ which is the algorithm I developed for panel detection. It saves a binary mask for panel per each band in the same folder for panel.
                    o	Pros: 
                        *	Sometimes the default algorithm is not able to detect the panel corners. 
                        *	It can detect the panel even if the panel images were captured by drone from less than 10 meter altitude. 
                    o	Cons:
                        *	It is slower than the default algorithm. 
    
    panel_capture_mode: if the panel_detection_mode is set to ‘my_func’, then user needs to define whether the panel capture mode was either ‘manual’ or ‘drone’.
                        In ‘manual’, pilot took the images manually per the instruction provided by Micasense. 
                        In ‘drone’ mode, pilot captured the images by flying at an altitude less than 10 meter above the ground. 
    
    save_as_geotiff: this is not active now. But the purpose is to save the stacked images with geotiff format.
    
    generateThumbnails: it stacks red, green, and blue bands and saves a RGB thumbnail (with small size) per each image set. 
    
    generateIndividualBands: it saves individual bands after performing all of the pre-processing. 
    
    overwrite: it overwrites the pre-processed images (stacked, individual bands, and thumbnails) if there is an image with the same name in the corresponding folder.
    
    envi_metadata: it saves metadata with ENVI format for each multispectral (stacked) image.
    
    pix4D_metadata: it saves a CSV metadata for all individual bands. 
    
    save_json: it extracts useful information from image metadata and saves them as a geojson file so we can open the captured images as points in QGIS/ArcGIS.



"""
import sys
# change this to the folder containing the codes
sys.path.append(r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master')

from micasense.Micasense_pre_processing_wrapper import pre_processing




image_path = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\Vineyard Matt\2019\Selma\19_5_8_vineyard_matt_selma_bloom\Images\MS - Manual Flight\images\test\images'

panel_path_before = None
panel_path_after = None


flight_alt = 16 # altitude (in meter) above the ground level
ground_alt = 91 # altitude of the ground level (in meter) above the sea level 
alignment_mat_path = r'G:\My Drive\Davis\Research\Python\MicaSense\Alignment Matrix\\alignment_micasense_15_120_m.pkl'
    
    
pre_processing(image_path,
                   alignment_mat_path,
                   flight_alt,
                   ground_alt = ground_alt,
                   panel_path_before=panel_path_before,
                   panel_path_after=panel_path_after,
                   panel_detection_mode = 'my_func',
                   panel_capture_mode = 'manual',
                   save_as_geotiff = False,
                   generateThumbnails = True,
                   generateIndividualBands = False,
                   overwrite = True,
                   envi_metadata = True,
                   pix4D_metadata = False,
                   save_json = True)