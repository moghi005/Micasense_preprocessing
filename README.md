# Radiometric calibration of multispectral images
This repository offers a python-based batch processing pipeline for radiometric calibration of multispectral images captured by RedEdge imager. An appropriate radiometric calibration process has two main steps: (i) converting raw images to radiance (Wm-2sr-1nm-1) to account for sensor-dependent factors such as non-uniform spatial and spectral responses of the sensor in the camera (e.g., gain, offset, and quantum efficiency), (ii) converting radiance images to reflectance to account for variation in intensity of incident light over time [(reference)](https://www.frontiersin.org/articles/10.3389/fpls.2018.01182/full#h3).
My goal was to develop a batch processing pipeline for radiometric calibration of multispectral images with more functionality and flexibility, so I developed several python scripts and borrowed/modified several codes from [Micasense GitHub](https://github.com/micasense/imageprocessing) repository.


# Installation
I highly recommend visit [Micasense repository](https://github.com/micasense/imageprocessing) where you can find informative [tutorials](https://micasense.github.io/imageprocessing/index.html) and helpful information about the installation of the required packages.

- To install the required packages, please refer to [setup](https://micasense.github.io/imageprocessing/MicaSense%20Image%20Processing%20Setup.html) page and follow their instruction based on the operating system on your machine.
- After installation and testing, please download/clone this repository.....

# Features
Users need to provide several inputs in `wrapper` to start batch processing. These inputs include:

- *alignment_mat_path*: a string variable, it is the path for a pickle file that contains the alignment matrices calculated for various altitudes.
- *image_path*: a string variable, it is the path to the folder that contains multispectral images. This folder can contain several sub folders.
- *panel_path_before*: a string variable, it is the path to the folder that contains the images of the panel captured BEFORE the flight. Only one set of image (5 bands) should be in this folder. If you don't have the panel images before the flight, you can set `panel_path_before = None`, therefore, only DLS data is used to convert the radiance images to reflectance. Alternatively, if you have panel images before the flight, the algorithm uses the panel images to calculate an in-situ factor to correct the irradiance derived from DLS data measured by downwelling sensor over the entire flight for each image set.
- *panel_path_after*: a string variable, it is the path to the folder that contains the images of the panel captured AFTER the flight. Only one set of image (5 bands) should be in this folder. This is just to check if we get the expected reflectance values from the panel (reflectance values provided by MicaSense for your panel) after applying all the preprocessing steps.

![test](/Demo/figures_for_readmefile/alignment_dictionary.png?raw=true "alignment matrices dictionary")
