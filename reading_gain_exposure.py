# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 12:39:08 2020

@author: Ali Moghimi
email: amoghimi@ucdavis.edu

"""

import sys
sys.path.append(r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master')
import pandas as pd
import micasense.metadata as metadata
import glob



def reading_gain_exposure(image_path, ms_ext='tif', sub_dir=False):
    
    columns = ['image', 'gain', 'exposure', 'dls_gain', 'dls_exposure']
    data_list = []

    if image_path.endswith(ms_ext) or image_path.endswith('tiff'): # loading only one image
        names_list = image_path
    elif sub_dir:
        names_list = [f for f in sorted(glob.glob(image_path +"/**/*."+ms_ext, recursive=True))]
    else:
        names_list = [f for f in sorted(glob.glob(image_path +"/*."+ms_ext, recursive=True))]
   
    
    for n, im in enumerate(names_list):
        
        meta = metadata.Metadata(im)
        name = meta.get_item('File:FileName')[:-4]
        gain = meta.get_item('XMP:Gain')
        exposure = meta.get_item('XMP:Exposure')
        dls_gain = meta.get_item('XMP:IrradianceGain')
        dls_exposure = meta.get_item('XMP:IrradianceExposureTime')
        
        row = [name, gain, exposure, dls_gain, dls_exposure]
        data_list.append(row)
        print('image {} out of {}'.format(n+1, len(names_list)))
        
    df = pd.DataFrame(data_list, index=None, columns=columns)
    
    return df