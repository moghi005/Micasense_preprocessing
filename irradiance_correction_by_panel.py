# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 15:45:53 2019
@author: Ali Moghimi
email:	amoghimi@ucdavis.edu


Irradiance_correction_by_panel Class
	
	what does this class do:
		It calculates a coefficient for irradiance correction based on the actual reflectance of the panel
		
	What do I need to change in this script?
		You need to change the this line: self.panel_actual_reflectance_by_band = [0.64, 0.65, 0.65, 0.60, 0.64]
		Enter the actual reference of the panel you have. Note the order is Blue, Green, Red, NIR, and RedEdge.
		

	input:
			path for a folder that contains only images (captured at 5 bands) of the reference panel
            
            'capture_mode' refers to the way images were captured. 
            
                capture_mode = 'manual' -- If the images were captured manually (taking drone by hand), the way Micasense recommend. 
                capture_mode = 'drone' --  If the images were captured while the drone was flying over the panel. 
"""


import numpy as np
import glob
#import os
import matplotlib.pyplot as plt
#import multiprocessing

import sys
sys.path.append(r'C:\Users\BAE User\Box\Digital Ag Lab\Codes\micasense_AliMoghimi')
#import micasense.imageset as imageset
import micasense.capture as capture
#from micasense.image import Image
from micasense.panel import Panel
import micasense.dls as dls

from micasense.panel_segmentation import panel_segmentation



class Irradiance_correction_by_panel():
    """
    a coefficient is calculated for irradiance correction based on the actual reflectance of panel
    """
    def __init__(self, panel_path, panel_detection_mode = 'default', panel_capture_mode = 'manual'):
        self.panel_path = panel_path
#        self.dls_correction = None
        self.panel_radiances = []
        self.panel_radiances_std = []
        self.n_panel_pixels = []
        self.n_saturated_pixels = []
        self.dls_irradiances = []
        self.center_wavelengths = []
        self.dls_correction_coeff = []
        self.mean_panel_reflectance = []
        self.panel_actual_reflectance_by_band = [0.64, 0.65, 0.65, 0.60, 0.64] # Our sensor
        
# ---------------------- Loading Panels----------------------------------------
        
        panel_names = [f for f in sorted(glob.glob(self.panel_path + "**/*.tif", recursive=True))]
        
        if len(panel_names) > 5:
            raise RuntimeError("Only one set of panel image, inlcuding five bands, should be provided. Check the panel folder")
            
        if len(panel_names) == 0:
            raise IOError("No files (*.tif) provided. Check the path to panel folder")
        
        self.panel_names = panel_names
        
# ---------------- Capture panels by capture class ----------------------------            
        self.cap = capture.Capture.from_filelist(panel_names)
        self.panel_corners = None
        
        
        if panel_detection_mode == 'default':
            self.panel_corners = self.corners()
        elif panel_detection_mode == 'my_func':
            self.panel_corners = self.my_corners_func(panel_capture_mode)
        else:
            raise IOError('panel detection mode should be either "default" or "my_func"')
            
       
# -------------- Segmenting panels by capture class ---------------------------    
        
    def corners(self):
        self.cap.detect_panels()
        panel_corners = [Panel.panel_corners(p) for p in self.cap.panels]
        self.panel_corners = panel_corners
        self.cap.panelCorners = panel_corners
        return panel_corners

#-------------- Segmenting panels by my function (panel_segmentation) -------            
    def my_corners_func(self, mode):
        panel_corners = panel_segmentation(self.panel_path, panel_capture_mode = mode)
        self.panel_corners = panel_corners
#        self.cap.panelCorners = panel_corners
        self.cap.set_panelCorners(panel_corners)
        self.cap.plot_panel_location(self.panel_names, panel_corners)
        return panel_corners

    
    # ---- converting panel image to radiance and extracting
    #       mean, std, num_pixels, num_saturated_pixels using the panel_corners ---

    def dn_to_radiance(self):
#        if self.panel_corners is None:
#            panel_corners = self.corners()
#            self.cap.set_panelCorners(panel_corners)
#            self.panel_corners = panel_corners
            
        panel_radiances_param = np.array(self.cap.panel_radiance())
        self.panel_radiances = panel_radiances_param[:, 0]
        self.panel_radiances_std = panel_radiances_param[:, 1]
        self.n_panel_pixels = panel_radiances_param[:, 2]
        self.n_saturated_pixels = panel_radiances_param[:, 3]
        
    
        for elem in self.n_saturated_pixels:
            if elem != 0:
                band_stau = int(np.where(self.panel_radiances_std/self.panel_radiances == elem)[0]) + 1
                print('WARNING: there is {} saturated pixels in band {}.'.format(int(elem) , band_stau))
                
        for cv in self.panel_radiances_std/self.panel_radiances:
            if cv >= 0.03:
                band_cv = int(np.where(self.panel_radiances_std/self.panel_radiances == cv)[0]) + 1
                print('WARNING: the coefficient of variation of radiance is {} for panel pixels in band {}.'.format(cv , band_cv))

# ---------------- Computing solar orientation --------------------------------
    
    """ 
    from the current position (lat,lon,alt) tuple
    and time (UTC), as well as the sensor orientation (yaw,pitch,roll) tuple
    compute a sensor sun angle - this is needed as the actual sun irradiance
    (for clear skies) is related to the measured irradiance by:
    
    I_measured = I_direct * cos (sun_sensor_angle) + I_diffuse
    For clear sky, I_direct/I_diffuse ~ 6 and we can simplify this to
    I_measured = I_direct * (cos (sun_sensor_angle) + 1/6)"""
    
    def dls_correction(self):
        
        self.dls_irradiances = [] # otherwise, it will append everytime the function is run
        self.center_wavelengths = []
        
        # Define DLS sensor orientation vector relative to dls pose frame
        dls_orientation_vector = np.array([0,0,-1])
        # compute sun orientation and sun-sensor angles
        (
            sun_vector_ned,    # Solar vector in North-East-Down coordinates
            sensor_vector_ned, # DLS vector in North-East-Down coordinates
            sun_sensor_angle,  # Angle between DLS vector and sun vector
            solar_elevation,   # Elevation of the sun above the horizon
            solar_azimuth,     # Azimuth (heading) of the sun
        ) = dls.compute_sun_angle(self.cap.location(),
                              self.cap.dls_pose(),
                              self.cap.utc_time(),
                              dls_orientation_vector)
    
        # ------------------ Correcting DLS readings for orientations -----------------
    
        # Since the diffuser reflects more light at shallow angles than at steep angles,
        # we compute a correction for this
        fresnel_correction = dls.fresnel(sun_sensor_angle)
        
        # Now we can correct the raw DLS readings and compute the irradiance on level ground

        for img in self.cap.images:
            dir_dif_ratio = 6.0
            percent_diffuse = 1.0/dir_dif_ratio
            # measured Irradiance / fresnelCorrection
            sensor_irradiance = img.spectral_irradiance / fresnel_correction
            untilted_direct_irr = sensor_irradiance / (percent_diffuse + np.cos(sun_sensor_angle))
            # compute irradiance on the ground using the solar altitude angle
            dls_irr = untilted_direct_irr * (percent_diffuse + np.sin(solar_elevation))
            self.dls_irradiances.append(dls_irr)
            self.center_wavelengths.append(img.center_wavelength)
    
   
    def radiance_to_reflectance(self, coef_in_situ=None):
        
        if coef_in_situ is None:
            self.coef_in_situ()
        else:
            self.dn_to_radiance()
            self.dls_correction()
            self.dls_correction_coeff = coef_in_situ
           
        self.cap.undistorted_reflectance(irradiance_list=self.dls_irradiances * self.dls_correction_coeff)
        self.mean_panel_reflectance = self.cap.panel_reflectance()
        
    def plot_reflectance(self):
        self.coef_in_situ()
        self.cap.plot_undistorted_reflectance(self.dls_irradiances * self.dls_correction_coeff) # Reflectance = (pi * radiance) / (dls_irradiances*dls_correction)

        
    """"
    ----------------------- Tying the camera and DLS together vis Panels ---------
    """
    
    def coef_in_situ(self):
        
        import math
        self.dn_to_radiance()
        self.dls_correction()
        irr_to_panel = math.pi * self.panel_radiances / self.panel_actual_reflectance_by_band # this is actual irradiance to the panel
        dls_correction_coeff = irr_to_panel/self.dls_irradiances
        self.dls_correction_coeff = dls_correction_coeff
        return dls_correction_coeff  


    def plot_panel_reflectance(self):
        self.radiance_to_reflectance()
        self.dls_correction()
        fig, axe1 = plt.subplots()
#        color_axe1 = 'tab:red'
        min_y = np.min([self.mean_panel_reflectance, self.panel_actual_reflectance_by_band]) - 0.05
        min_y = round(min_y*100)/100
        max_y = np.max([self.mean_panel_reflectance, self.panel_actual_reflectance_by_band]) + 0.05
        max_y = round(max_y*100)/100
        axe1.scatter(self.center_wavelengths, self.panel_actual_reflectance_by_band, color='r')
        axe1.set_xlabel('Wavelength (nm)')
        axe1.set_ylabel('Reflectance of panel (%)', color='k')
        axe1.tick_params(axis='y', labelcolor='k')
        axe1.set_ylim(min_y, max_y)

        axe1.scatter(self.center_wavelengths, self.mean_panel_reflectance, color='g')
        
        labels = ['actual', 'measured']
        fig.legend(labels)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
        
    def plot_coef_in_situ(self):
        self.coef_in_situ()
        fig, ax = plt.subplots()
        ax.scatter(self.center_wavelengths, self.dls_correction_coeff )

        
# ---------- ploting segmented panels by my function added to catpure class ---
        
    def plot_panel_location(self):
        if self.panel_corners is None: # it means that panel_corners haven't been computed yet (by my_corners_func)
            self.panel_corners = self.corners()
        self.cap.plot_panel_location(self.panel_names, self.panel_corners)

    def plot_redi_irradi(self):
        self.dn_to_radiance()
        self.dls_correction()
        fig, axe1 = plt.subplots()
#        color_axe1 = 'tab:red'
        axe1.scatter(self.center_wavelengths,self.dls_irradiances, color='r')
        axe1.set_xlabel('Wavelength (nm)')
        axe1.set_ylabel('Irradiance ($W/m^2/nm$)', color='r')
        axe1.tick_params(axis='y', labelcolor='r')
        
        axe2 = axe1.twinx() # instantiate a second axes that shares the same x-axis
#        color_axe2 = 'tab:blue'
        axe2.scatter(self.center_wavelengths,self.panel_radiances, color='b')
        axe2.set_ylabel('Radiance ($W/m^2/nm$)', color='b')
        axe2.tick_params(axis='y', labelcolor='b')

        labels = ['dls irradiances', 'panel_radiances']
        fig.legend(labels)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()