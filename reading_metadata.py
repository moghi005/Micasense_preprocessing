# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 15:00:36 2019

@author: coeadmin-amoghimi
"""
import sys
sys.path.append(r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master')
import micasense.imageset as imageset
import pandas as pd
import micasense.metadata as metadata

def reading_metadata(image_folder=None, image_name=None):
    
    if image_folder:
        imlist = imageset.ImageSet.from_directory(image_folder)
        data, columns = imlist.as_nested_lists()
        meta_file = pd.DataFrame.from_records(data, index='imageName', columns=columns)
    
    if image_name:
        m = metadata.Metadata(image_name[0])
        meta_file = m.get_all()
    
    return meta_file
    