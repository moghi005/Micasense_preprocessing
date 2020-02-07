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
    
    reference_panel: it can be one of the following options:
                        * 'micasense':  the algorithm autamatically detec the panel and uses the micasense panel to compute or refine IRRADIANCE. 
                        * 'tarp_26':    Users need to draw a rectangle of the tarp images for all bands. The algrightm then uses the tarp reflectivity to compute or refine IRRADIANCE. 
                        * 'tarp_24':    Similar to 'tarp_26', however, the algorithm uses the reflectivity of tarp_24 to compute ir refine IRRADIANCE.
                        
    reflectance_convert_mode:  it can be one of the following options:
                                        * 'panel_dls': using panel before to correct the irradiance of DLS. NOTE: it can be tarp as well. 
                                        * 'panel':      using only panel to compute irradiance and use the colculated irradiance for reflectance conversion. 
                                        * 'dls':        using only DLS data for reflectance conversion. NOTE: it is similar to the case when the 'panel_before' is not provided, the algorirthm uses only DLS data.
                                        
                                        NOTE: in all cases, DN is first converted to radiance and then to reflectance. 
                                        
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
code_path = r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master'
sys.path.append(code_path)
import os
from micasense.Micasense_pre_processing_wrapper import pre_processing


alignment_mat_path = r'G:\My Drive\Davis\Research\Python\MicaSense\Alignment Matrix\\alignment_micasense_10_120_m.pkl'

image_path = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\RedEdge Camera and DLS Experiments\Radiometric calibration tests\Data\20-2-4 - Experiment 3 - Two Tarps\Reflectance\tarp_26_radiance_ref\tarp_images'
panel_path_before = r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\RedEdge Camera and DLS Experiments\Radiometric calibration tests\Data\20-2-4 - Experiment 3 - Two Tarps\Reflectance\tarp_26_radiance_ref\tarp_before'
panel_path_after = None #r'C:\Users\coeadmin-amoghimi\Box\Digital Ag Lab\Aerial\RedEdge Camera and DLS Experiments\Radiometric calibration tests\Data\20-2-4 - Experiment 3 - Two Tarps\panel_after\panel_after'
flight_alt = 10                     # altitude (in meter) above the ground level
reference_panel = 'tarp_26'       # 'micasense' or 'tarp_26 or tarp_24' 
panel_detection_mode = 'my_func'    # or 'default'
panel_capture_mode = 'manual'
reflectance_convert_mode = 'panel' # 'panel_dls', or 'panel', or 'dls'

ground_alt = None

if flight_alt is None and ground_alt is None:
    band_name = 'plot_9_1.tif' # define the name of an image (band) in the image_path folder
    band_path = os.path.join(image_path, band_name)
    size_obj = 0.15 # size of the object along horizon (x direction) in meter
    FOV = 47.2
    from micasense.ground_asl import ground_asl
    ground_alt = ground_asl(band_path, size_obj, FOV) # altitude of the ground (in meter) above the sea level 



pre_processing(
               alignment_mat_path = alignment_mat_path,
               image_path = image_path,
               flight_alt = flight_alt,
               ground_alt = ground_alt,
               panel_path_before = panel_path_before,
               panel_path_after = panel_path_after,
               reference_panel = reference_panel,
               panel_detection_mode = panel_detection_mode,
               panel_capture_mode = panel_capture_mode,
               reflectance_convert_mode=reflectance_convert_mode,
               save_as_geotiff = False,
               generateThumbnails = True,
               generateIndividualBands = False,
               overwrite = True,
               envi_metadata = True,
               pix4D_metadata = True,
               save_json = True)
    
