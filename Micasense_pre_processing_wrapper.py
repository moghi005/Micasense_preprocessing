# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 16:22:41 2019

@author: Ali Moghimi
email:	amoghimi@ucdavis.edu







"""

# -------------------------       importing the required packages 

import sys
# change this to the folder containing the codes
sys.path.append(r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master')
import os
import numpy as np
import pandas as pd

import micasense.imageset as imageset
import micasense.capture as capture
import micasense.image as image
import micasense.irradiance_correction_by_panel as correction
from micasense.save_metadata import saveMetadata

#import exiftool
#import micasense.imageset as imageset
#from micasense.panel import Panel
#import micasense.dls as dls


# --------------------------    parameters that user needs to define

def pre_processing(image_path,
                   alignment_mat_path,
                   flight_alt,
                   panel_path_before=None,
                   panel_path_after=None,
                   panel_detection_mode = 'default',
                   panel_capture_mode = 'manual',
                   save_as_geotiff = False,
                   generateThumbnails = True,
                   generateIndividualBands = True,
                   overwrite = False,
                   envi_metadata = True,
                   pix4D_metadata = True,
                   save_json = True):

    
    # In[]
    
    # ------------- loading the alignment matrices for various altitude -----------
    
    import pickle
#    alignment_mat_path = r"C:\Users\BAE User\Box\Digital Ag Lab\Codes\micasense_AliMoghimi\alignment_matrix\alignment_micasense_attempt_4_green_pyramid0.pkl"
    pickle_in = open(alignment_mat_path,"rb")
    alignment_micasense = pickle.load(pickle_in)
    alt_align_mat_measured = [15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    
    # In[]
    # ------------ setting the folders for saving the outputs ---------------------
    
    outputPath_for_stacked = os.path.join(image_path,'..','stacks')
    if not os.path.exists(outputPath_for_stacked):
        os.makedirs(outputPath_for_stacked)
    
    if generateThumbnails:
        thumbnailPath = os.path.join(outputPath_for_stacked, '..', 'thumbnails')
        if not os.path.exists(thumbnailPath):
            os.makedirs(thumbnailPath)
    
    # In[]
    #---------------- correcting the irradiance measured by DLS -------------------
    if panel_path_before:
        irr_correction = correction.Irradiance_correction_by_panel(panel_path_before, panel_detection_mode = panel_detection_mode, panel_capture_mode = panel_capture_mode)
        
        irr_correction.radiance_to_reflectance()
        mean_panel_ref = irr_correction.mean_panel_reflectance
        print('panel reflectance before flight: {}'.format(mean_panel_ref)) # it should match with the actual reflectance of the panel
        
        dls_coef = irr_correction.coef_in_situ() 
    
    else:
        dls_coef = np.array([1, 1, 1, 1, 1]) 
    
    # some optional parameters:
    
    #panel_corners = irr_correction.panel_corners
    #irr_correction.radiance_to_reflectance()
    #irr_correction.center_wavelengths
    #irr_correction.plot_panel_reflectance()
    #irr_correction.plot_coef_in_situ()
    #irr_correction.plot_panel_location()
    #irr_correction.plot_redi_irradi()
    #dls_irr = []
    #dls_pos = []
    #for b in range(5):
    #    dls_irr.append(irr_correction.cap.images[b].meta.spectral_irradiance())
    #    dls_pos.append(irr_correction.cap.images[b].meta.dls_pose())
     
# In[]:
    #---------------- Checking the coef-in-situ by panel images after flight  -------------------
    
    ''' using the dls_coef calculated based on the panel image taken pre flight to calculate the reflectance
    of the panel image taken post flight - I expect the reflectance of the panel after flight to be close
    to the actual values when we use the dls_coef'''
    
    if panel_path_after:
        irr_correction_after = correction.Irradiance_correction_by_panel(panel_path_after, panel_detection_mode = panel_detection_mode, panel_capture_mode = panel_capture_mode)
        irr_correction_after.radiance_to_reflectance(dls_coef)
        mean_panel_ref_after_with_coef = irr_correction_after.mean_panel_reflectance
        print('panel reflectance after flight: {}'.format(mean_panel_ref_after_with_coef)) # it should be close to the actual reflectance of the panel
            
        
        ''' if we don't use any in_situ coef (i.e. only use DLS data), then this is the result:'''
        no_dls_coef = np.array([1, 1, 1, 1, 1])
        irr_correction_after.radiance_to_reflectance(no_dls_coef)
        mean_panel_ref_after_no_coef = irr_correction_after.mean_panel_reflectance
        print('panel reflectance after flight using only DLS data: {}'.format(mean_panel_ref_after_no_coef)) # it should match with the actual reflectance of the panel
        
        ''' calculating the in_situ coef based on the panel image taken after flight. I expect these coefficient 
        to be similar to the dls_coef calculated based on the panel image taken before flight'''
        irr_correction_after.radiance_to_reflectance()
        mean_panel_ref_after = irr_correction_after.mean_panel_reflectance
        print(mean_panel_ref_after) # it should match with the actual reflectance of the panel
        dls_coef_after = irr_correction_after.coef_in_situ() 

    
    # In[]:
    # -------------- loading the list of images from the given folder -------------
    
    imlist = imageset.ImageSet.from_directory(image_path)
    
    # -------------- convert the imagelist to Panda data frame --------------------
    
    data, columns = imlist.as_nested_lists()
    df = pd.DataFrame.from_records(data, index='capture_id', columns=columns)
    df['altitude'] = flight_alt 
    
#    print("in total {} set of images were loaded.".format())
    
    # In[]
    #------------------- save a report for the code ----------------------------
    
    head_report, tail = os.path.split(image_path)
    outputNameReport = head_report + "\\Report.txt"
    with open(outputNameReport, "w") as report:
        out_string = ""
        out_string += 'total number of images: {}'.format(len(df))
        out_string += '\n ----------------------------------------------------'
        out_string += '\n'
        out_string += '\n'
        if panel_path_before:       
            out_string += 'panel reflectance before flight: {}'.format([round(item, 2) for item in mean_panel_ref])
            out_string += '\n ----------------------------------------------------'
            out_string += '\n'
            out_string += '\n'
        else:
            out_string += 'Only DLS data was used for reflectance conversion, no panel was used!'
            out_string += '\n ----------------------------------------------------'
            out_string += '\n'
            out_string += '\n'            
                
        if panel_path_after:
            out_string += 'panel reflectance after flight: {}'.format([round(item, 2) for item in mean_panel_ref_after_with_coef])
            out_string += '\n ----------------------------------------------------'
            out_string += '\n'
            out_string += '\n'
        else:
            out_string += 'No panel images captured after the flight were provided by user!'
            out_string += '\n ----------------------------------------------------'
            out_string += '\n'
            out_string += '\n'
            
        out_string += 'in_situ coeff used for DLS correction: {}'.format([round(item, 3) for item in dls_coef])
        out_string += '\n ----------------------------------------------------'
        out_string += '\n'
        out_string += '\n'
        report.write(out_string)
        
    # In[ ]:
    # saves df as a geojson so we can use QGIS/ArcGIS to open the captured  images as points with the properties defined in 'column' variable 
    
    if save_json:
        
        path_for_json = os.path.join(outputPath_for_stacked,'..','json')
        if not os.path.exists(path_for_json):
            os.makedirs(path_for_json)
        from mapboxgl.utils import df_to_geojson
        geojson_data = df_to_geojson(df,lat='latitude',lon='longitude')
    
        with open(os.path.join(path_for_json,'imageSet.json'),'w') as f:
            f.write(str(geojson_data))
     
    # In[ ]:
    
    
    #try:
    #    irradiance = panel_irradiance+[0]
    #except NameError:
    #    irradiance = None
    
    
    import datetime
    start = datetime.datetime.now()
    
    for i,cap in enumerate(imlist.captures):
        
        delta_alt = abs(np.array(alt_align_mat_measured) - flight_alt)
        if np.min(delta_alt) < 5:
            ind = int(np.where(delta_alt==np.min(delta_alt))[0])
            alt_align_close_to_flight_alt = alt_align_mat_measured[ind]
            warp_matrices = [alignment_micasense[alt_align_close_to_flight_alt][band] for band in alignment_micasense[alt_align_close_to_flight_alt]]
        else:
            raise IOError('Error: could not find a proper alignment matrix for this altitue!')
                
        image_name_blue = cap.images[0].meta.get_item("File:FileName")
        image_name = image_name_blue[0:-6] # remove '_1.tif'
        outputFilename = image_name+'.tif'
        
        full_outputPath_for_stacked = os.path.join(outputPath_for_stacked, outputFilename)
        
        if (not os.path.exists(full_outputPath_for_stacked)) or overwrite:
            if(len(cap.images) == len(imlist.captures[0].images)):
                irradiance = dls_coef * cap.dls_irradiance()
                cap.create_aligned_capture(irradiance_list=irradiance, warp_matrices = warp_matrices) # convert to reflectance
                
                if save_as_geotiff:
                    cap.save_capture_as_stack_gtif(full_outputPath_for_stacked, flight_alt, generateIndividualBands=generateIndividualBands)
                else:
                    cap.save_capture_as_stack(full_outputPath_for_stacked, generateIndividualBands=generateIndividualBands)
                
                if generateThumbnails:
                    thumbnailFilename = image_name + '.jpg'
                    fullThumbnailPath= os.path.join(thumbnailPath, thumbnailFilename)
                    cap.save_capture_as_rgb(fullThumbnailPath)
        cap.clear_image_data()
    
        # save Metadata
      
        save_meta = saveMetadata(cap, outputPath_for_stacked)
        save_meta.save_metadata_pix4D(outputPath_for_stacked, mode = 'stack')
        
        if envi_metadata:
            save_meta.save_metadata_envi()
        if pix4D_metadata:
            head_csv, tail_csv = os.path.split(image_path)
            csv_path = os.path.join(head_csv,'individual_bands')
            if not os.path.exists(csv_path):
                os.makedirs(csv_path)
            save_meta.save_metadata_pix4D(csv_path, mode = 'individual')
            
    #    update_f2(float(i)/float(len(imgset.captures)))
    #update_f2(1.0)
    end = datetime.datetime.now()
    
    print("Saving time: {}".format(end-start))
    print("Alignment+Saving rate: {:.2f} images per second".format(float(len(imlist.captures))/float((end-start).total_seconds())))
        
## In[]:
#
##Use Exiftool from the command line to write metadata to images
#    
#import subprocess
#
#old_dir = os.getcwd()
#os.chdir( outputPath_for_stacked)
#cmd = 'exiftool -csv="{}" -overwrite_original .'.format(fullCsvPath)
#print(cmd)
#try:
#    subprocess.check_call(cmd)
#finally:
#    os.chdir(old_dir)
#    
## In[]
#
#import cv2
#import numpy as np
#import matplotlib.pyplot as plt
#import micasense.imageutils as imageutils
#import micasense.plotutils as plotutils
#
#match_index = 1 # Index of the band (Green was a better option than rededge)
#img_type = 'reflectance'
#warp_mode = cv2.MOTION_HOMOGRAPHY # MOTION_HOMOGRAPHY or MOTION_AFFINE. For Altum images only use HOMOGRAPHY
#cropped_dimensions, edges = imageutils.find_crop_bounds(cap, warp_matrices, warp_mode=warp_mode)
#
#im_aligned = imageutils.aligned_capture(cap, warp_matrices, warp_mode, cropped_dimensions, match_index, img_type=img_type)
#
## In[]    
#figsize=(16,13)   # use this size for export-sized display
#
#rgb_band_indices = [2,1,0]
#cir_band_indices = [3,2,1]
#
## Create a normalized stack for viewing
#im_display = np.zeros((im_aligned.shape[0],im_aligned.shape[1],im_aligned.shape[2]), dtype=np.float32 )
#
#im_min = np.percentile(im_aligned[:,:,rgb_band_indices].flatten(), 0.5)  # modify these percentiles to adjust contrast
#im_max = np.percentile(im_aligned[:,:,rgb_band_indices].flatten(), 99.5)  # for many images, 0.5 and 99.5 are good values
#
## for rgb true color, we use the same min and max scaling across the 3 bands to 
## maintain the "white balance" of the calibrated image
#for i in rgb_band_indices:
#    im_display[:,:,i] =  imageutils.normalize(im_aligned[:,:,i], im_min, im_max)
#
#rgb = im_display[:,:,rgb_band_indices]
#
## for cir false color imagery, we normalize the NIR,R,G bands within themselves, which provides
## the classical CIR rendering where plants are red and soil takes on a blue tint
#for i in cir_band_indices:
#    im_display[:,:,i] =  imageutils.normalize(im_aligned[:,:,i])
#
#cir = im_display[:,:,cir_band_indices]
#fig, axes = plt.subplots(1, 2, figsize=figsize)
#axes[0].set_title("Red-Green-Blue Composite")
#axes[0].imshow(rgb)
#axes[1].set_title("Color Infrared (CIR) Composite")
#axes[1].imshow(cir)
#plt.show()
#
## In[6]
## Create an enhanced version of the RGB render using an unsharp mask
#gaussian_rgb = cv2.GaussianBlur(rgb, (9,9), 10.0)
#gaussian_rgb[gaussian_rgb<0] = 0
#gaussian_rgb[gaussian_rgb>1] = 1
#unsharp_rgb = cv2.addWeighted(rgb, 1.5, gaussian_rgb, -0.5, 0)
#unsharp_rgb[unsharp_rgb<0] = 0
#unsharp_rgb[unsharp_rgb>1] = 1
#
## Apply a gamma correction to make the render appear closer to what our eyes would see
#gamma = 1.4
#gamma_corr_rgb = unsharp_rgb**(1.0/gamma)
#fig = plt.figure(figsize=figsize)
#plt.imshow(gamma_corr_rgb, aspect='equal')
#plt.axis('off')
#plt.show()
#
## In[]
#import imageio
#imtype = 'png' # or 'jpg'
#imageio.imwrite('rgb.'+imtype, (255*gamma_corr_rgb).astype('uint8'))
#imageio.imwrite('cir.'+imtype, (255*cir).astype('uint8'))
#
#
#
#
#
#
#
#    
#
#
## In[]
## ----------------------------------------------------------------------------
#import numpy as np
#import matplotlib.pyplot as plt
## conda install -c anaconda basemap
#from mpl_toolkits.basemap import Basemap
#
#lat = np.array(df.iloc[:]['latitude'])
#lon = np.array(df.iloc[:]['longitude'])
#alt = np.array(df.iloc[:]['altitude'])
#
#ll_lat = np.floor(min(lat)*10**2)/10**2
#ll_lon = np.floor(min(lon)*10**2)/10**2
#
#ur_lat = np.ceil(max(lat)*10**2)/10**2
#ur_lon = np.ceil(max(lon)*10**2)/10**2
#
#
#fig = plt.figure(figsize=(8, 8))
## State of California
#m = Basemap(projection='lcc', resolution='h', 
#            lat_0=37.5, lon_0=-119,
#            width=1E6, height=1.2E6)
#
##m = Basemap(projection='mill', resolution='h', 
##            llcrnrlon=ll_lon, llcrnrlat=ll_lat,
##            urcrnrlon=ur_lon, urcrnrlat=ur_lat)
#
##m = Basemap(projection='mill', resolution='h', 
##            llcrnrlon=-120, llcrnrlat=35,
##            urcrnrlon=-118, urcrnrlat=37)
#
#
#m.bluemarble()
##m.shadedrelief()
##m.drawcoastlines(color='gray')
##m.drawcountries(color='gray')
#m.drawstates(color='red')
#
## 2. scatter city data, with color reflecting population
## and size reflecting area
#m.scatter(lon, lat, latlon=True,
#          c=np.log10(alt),
#          cmap='Reds', alpha=0.5)
#
## 3. create colorbar and legend
#plt.colorbar(label=r'$\log_{10}({\rm population})$')
#plt.clim(3, 7)

