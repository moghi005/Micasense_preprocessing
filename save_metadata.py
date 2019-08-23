# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 14:10:14 2019

@author: coeadmin-amoghimi
"""

import sys
sys.path.append(r'G:\My Drive\Davis\Research\Python\MicaSense\imageprocessing-master')
import os 
import micasense.capture as capture
import builtins



header = "ImageName,\
Latitude (decimal degrees),Longitude (decimal degrees),Altitude_ASL,\
Roll (degrees), Pitch (degrees), Yaw (decimal degrees),\
Gian, Exposure, FNumber,\
GPSDateStamp,GPSTimeStamp,\
GPSLatitude,GpsLatitudeRef,\
GPSLongitude,GPSLongitudeRef,\
GPSAltitude,GPSAltitudeRef,\
FocalLength,\
ImagePath\n"

#header = "ImageName,\
#Latitude (decimal degrees),Longitude (decimal degrees),Altitude_ASL,\
#Roll (degrees), Pitch (degrees), Yaw (decimal degrees),\
#Gian, Exposure, FNumber,\
#GPSDateStamp,GPSTimeStamp,\
#GPSLatitude,GpsLatitudeRef,\
#GPSLongitude,GPSLongitudeRef,\
#GPSAltitude,GPSAltitudeRef,\
#FocalLength,\
#XResolution,YResolution,ResolutionUnits,\
#ImagePath\n"

hdr_envi = {} 

#labels = ['byte order', 'bands']

lines = [header]

class saveMetadata():
    """ saves metadata with two formats:
            1- csv for pix4D
            2- ENVI for other remote sensing software """
    
    
    def __init__(self, cap, outputPath):
        self.cap = cap
        self.outputPath = outputPath
        
    def save_metadata_pix4D(self, csv_path=None):
        
        if csv_path is None:
            csv_path = self.outputPath
        
        lat,lon,alt = self.cap.location()
    
        latdeg, latmin, latsec = decdeg2dms(lat)
        londeg, lonmin, lonsec = decdeg2dms(lon)
        latdir = 'North'
        if latdeg < 0:
            latdeg = -latdeg
            latdir = 'South'
        londir = 'East'
        if londeg < 0:
            londeg = -londeg
            londir = 'West'
            
#        resolution = self.cap.images[0].focal_plane_resolution_px_per_mm
        
        for band in range(len(self.cap.images)):
#        linestr = '"{}",'.format(self.cap.images[0].meta.get_item("File:FileName")[0:-6]) # remove '_1.tif'
            linestr = '"{}",'.format(self.cap.images[band].meta.get_item("File:FileName")) 
    
            
            linestr += '"{}",'.format(lat)
            linestr += '"{}",'.format(lon)
            linestr += '"{}",'.format(alt)
            
            linestr += '"{}",'.format(self.cap.images[band].meta.get_item("XMP:Roll"))
            linestr += '"{}",'.format(self.cap.images[band].meta.get_item("XMP:Pitch"))
            linestr += '"{}",'.format(self.cap.images[band].meta.get_item("XMP:Yaw"))
            
            linestr += '"{}",'.format(self.cap.images[band].meta.get_item("XMP:Gain"))
            linestr += '"{}",'.format(self.cap.images[band].meta.get_item("XMP:Exposure"))
            linestr += '"{}",'.format(self.cap.images[band].meta.get_item("EXIF:FNumber"))
        
            linestr += self.cap.utc_time().strftime("%Y:%m:%d,%H:%M:%S,")
            linestr += '"{:d} deg {:d}\' {:.2f}"" {}",{},'.format(int(latdeg),int(latmin),latsec,latdir[0],latdir)
            linestr += '"{:d} deg {:d}\' {:.2f}"" {}",{},{:.1f}, Above Sea Level (m),'.format(int(londeg),int(lonmin),lonsec,londir[0],londir,alt)
            linestr += '{:.2f},'.format(self.cap.images[band].focal_length)
#            linestr += '{},{},mm,'.format(resolution,resolution)
                    
            linestr += '"{}",'.format(self.outputPath)
            linestr += '\n' # when writing in text mode, the write command will convert to os.linesep
            
            lines.append(linestr)
        
            fullCsvPath = os.path.join(csv_path,'Pix4D.csv')
            with open(fullCsvPath, 'w') as csvfile: #create CSV
                csvfile.writelines(lines)    
            
    def save_metadata_envi(self):
            
#            hdr_envi['ENVI'] = 'ENVI'
            hdr_envi['sensor type'] = 'Micasense RedEdge'
            im_name = self.cap.images[0].meta.get_item("File:FileName")[0:-6]
            hdr_envi['image name'] = im_name 
            hdr_envi['interleave'] = 'tif'
            hdr_envi['samples'] = self.cap.images[0].meta.get_item("EXIF:ImageWidth")
            hdr_envi['lines'] = self.cap.images[0].meta.get_item("EXIF:ImageHeight")
            hdr_envi['bands'] = int(5) 
            hdr_envi['bit depth'] = self.cap.images[0].meta.get_item("EXIF:BitsPerSample")
            hdr_envi['data type'] = int(5) # float 64
            hdr_envi['shutter'] = self.cap.images[0].meta.get_item("Composite:ShutterSpeed")
            hdr_envi['expoture'] = self.cap.images[0].meta.get_item("EXIF:ExposureTime")
            hdr_envi['gain'] = self.cap.images[0].meta.get_item("XMP:Gain")
            hdr_envi['roll'] = self.cap.images[0].meta.get_item("XMP:Roll")
            hdr_envi['pitch'] = self.cap.images[0].meta.get_item("XMP:Pitch")
            hdr_envi['yaw'] = self.cap.images[0].meta.get_item("XMP:Yaw")
            hdr_envi['byte order'] = int(0)
            hdr_envi['header offset'] = int(0)
            hdr_envi['wavelength'] = [475, 560, 668, 840, 717]
            hdr_envi['fwhm'] = [20, 20, 10, 40, 10]
            
            name_with_extension = im_name + '.hdr'
            name_to_save = os.path.join(self.outputPath, name_with_extension)
            write_envi_header(name_to_save, hdr_envi, is_library=False)


 
def decdeg2dms(dd):
   is_positive = dd >= 0
   dd = abs(dd)
   minutes,seconds = divmod(dd*3600,60)
   degrees,minutes = divmod(minutes,60)
   degrees = degrees if is_positive else -degrees
   return (degrees,minutes,seconds)

      
def write_envi_header(fileName, header, is_library=False):
    fout = builtins.open(fileName, 'w')
    d = {}
    d.update(header)
    if is_library:
        d['file type'] = 'ENVI Spectral Library'
    elif 'file type' not in d:
        d['file type'] = 'ENVI Standard'
    fout.write('ENVI\n')
    # Write the standard parameters at the top of the file
    std_params = ['description', 'file type', 'sensor type', 'image name', 'samples', 'lines', 'bands',
                  'header offset','data type', 'interleave', 'byte order', 
                  'reflectance scale factor', 'map info']
    for k in std_params:
        if k in d:
            _write_header_param(fout, k, d[k])
    for k in d:
        if k not in std_params:
            _write_header_param(fout, k, d[k])
    fout.close()
    
    
def _write_header_param(fout, paramName, paramVal):
    
    if paramName.lower() == 'description':
        valStr = '{\n%s}' % '\n'.join(['  ' + line for line
                                       in paramVal.split('\n')])
    elif not isinstance(paramVal, (str, bytes)) and hasattr(paramVal, '__len__'):
        valStr = '{ %s }' % (
            ' , '.join([str(v).replace(',', '-') for v in paramVal]),)
        
    elif paramName.lower() == 'wavelength':
        valStr = '{%s}' % ' '.join([str(elem) for elem in paramVal])
    
    elif paramName.lower() == 'fwhm':
        valStr = '{%s}' % ' '.join([str(elem) for elem in paramVal])

    else:
        valStr = str(paramVal)
        
    fout.write('%s = %s\n' % (paramName, valStr))
            

            
            
