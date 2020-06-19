# Radiometric calibration of multispectral images
This repository offers a python-based batch processing pipeline for radiometric calibration of multispectral images captured by RedEdge imager. An appropriate radiometric calibration process has two main steps: (i) converting raw images to radiance (Wm-2sr-1nm-1) to account for sensor-dependent factors such as non-uniform spatial and spectral responses of the sensor in the camera (e.g., gain, offset, and quantum efficiency), (ii) converting radiance images to reflectance to account for variation in intensity of incident light over time [(reference)](https://www.frontiersin.org/articles/10.3389/fpls.2018.01182/full#h3).
My goal was to develop a batch processing pipeline for radiometric calibration of multispectral images with more functionality and flexibility, so I developed several python scripts and borrowed/modified several codes from [Micasense GitHub](https://github.com/micasense/imageprocessing) repository.


# Installation
I highly recommend visiting [Micasense repository](https://github.com/micasense/imageprocessing) where you can find informative [tutorials](https://micasense.github.io/imageprocessing/index.html) and helpful information about the installation of the required packages.

- To install the required packages, please refer to [setup](https://micasense.github.io/imageprocessing/MicaSense%20Image%20Processing%20Setup.html) page and follow their instruction based on the operating system on your machine.
- After following the installation guide and testing the installation, please download/clone this repository.

# Features
Users need to provide several inputs in `wrapper` to start batch processing. These inputs include:

- *alignment_mat_path*: a string variable, it is the path for a pickle file that contains the alignment matrices calculated for various altitudes. For more information on how to make the alignment matrix for each band, please refer to [alignment matrix]() page.
<!-- ![test](Demo/figures_for_readmefile/alignment_dictionary.png?raw=true "alignment matrices dictionary") -->
- *flight_alt*: above ground altitude (in meter) at which the UAV flew. This is required to use an appropriate alignment matrix for stacking the bands. if pilot flew manually and it was hard to keep the flight alt consistent so you are not sure about the flight altitude for each image, set `flight_alt = None`. In this case, you need to define *ground_alt* above the sea level, so the algorithm subtracts the altitude read by GPS from the ground alt to calculate the flight alt.
- *ground_alt*: ground altitude above the sea level. Define this only if you didn't define *flight_alt*. If you don't define *flight_alt* and *ground_alt*, the algorithm has a functionality to calculate ground_alt based on the field of view (FOV) and size of a known object in one of the images (such as panel). In this case, user should define the FOV of the sensor, *size_obj* which refers to the size of a known object along horizon (x direction) in meter. To specify the object, user should provide *band_name* which refers to the name of an image that contains the object, only one band is required. The image is shown and user need to draw a rectangle around the object of interest. The algorithm then calculates pixel size (spatial resolution) using the number of pixels in the rectangle drawn by user and the size of the object along horizon. Using FOV and the calculated spatial resolution, the algorithm calculates the flight altitude above the ground. By subtracting above ground alt from recorded alt by GPS, the ground level altitude is calculated.
- *image_path*: a string variable, it is the path to the folder that contains multispectral images. This folder can contain several sub folders.
- *panel_path_before*: a string variable, it is the path to the folder that contains the images of the panel captured BEFORE the flight. Only one set of image (5 bands) should be in this folder. If you don't have the panel images before the flight, you can set `panel_path_before = None`, therefore, only DLS data is used to convert the radiance images to reflectance. Alternatively, if you have panel images before the flight, the algorithm uses the panel images to calculate an in-situ factor to correct the irradiance derived from DLS data measured by downwelling sensor over the entire flight for each image set.
- *panel_path_after*: a string variable, it is the path to the folder that contains the images of the panel captured AFTER the flight. Only one set of image (5 bands) should be in this folder. This is just to check if we get the expected reflectance values from the panel (reflectance values provided by MicaSense for your panel) after applying all the preprocessing steps.
- *panel_detection_mode*: there are two options:

        1. ‘default’ which is the Micasense algorithm for panel detection using the QR code.
        2. ‘my_func’ which is the algorithm I developed for panel detection. It detects the panel and saves a binary mask for panel per each band in the same panel folder (i.e., panel_path_before)
                o	Pros:
                    *	Sometimes the default algorithm is not able to detect the panel corners.
                    *	It can detect the panel even if the panel images were captured by drone up to about 10 meter altitude.
                o	Cons:
                    *	It is slower than the default algorithm.
    **NOTE**: if you set `panel_capture_mode = 'my_func'`, you need to define *panel_capture_mode*.                 
- *panel_capture_mode*: if the panel_detection_mode is set to ‘my_func’, then user needs to define whether the panel capture mode was ‘manual’ (with the same procedure as MicaSense recommends) or ‘drone’ (with flying over the panel with an altitude less than 10 meter).
        1. In ‘manual’, pilot took the images manually per the instruction provided by Micasense.
        2. In ‘drone’ mode, pilot captured the images by flying at an altitude less than about 10 meter above the ground.
- *reference_panel*: A string variable that indicates which type of reference panel was used in the current mission. It can be one of the following options:

        * 'micasense': the algorithm automatically detects the panel and uses the micasense panel to compute or refine IRRADIANCE.
        * 'tarp_26': In this case, users need to draw a rectangle of the tarp (with 26% reflectivity) images for all bands. The algorithm then uses the tarp reflectivity to compute or refine IRRADIANCE.
        * 'tarp_24': Similar to 'tarp_26', however, the algorithm uses the reflectivity of tarp_24 (with 24% reflectivity) to compute or refine IRRADIANCE.
    **NOTE**: Users can use any tarp with any reflectivity, however, they need to revise `irradiance_correction_by_panel.py` accordingly.

- *reflectance_convert_mode*:  it can be one of the following options:

        * 'panel_dls': using panel images captured before flight to correct the irradiance of DLS. NOTE: it can be  tarp as well.
        * 'panel': using only panel to compute irradiance and using the calculated irradiance for reflectance conversion.
        * 'dls': using only DLS data for reflectance conversion. NOTE: it is similar to the case when the 'panel_before' is not provided, the algorithm uses only DLS data.
   **NOTE**: in all cases, DN is first converted to radiance and then to reflectance.          
- *save_as_geotiff*:  if `True`, it saves the stacked images with geotiff format. This is not active now. But the purpose is to save the stacked geoTIFF images.
- *generateThumbnails*: if `True`, it stacks red, green, and blue bands and saves a RGB thumbnail (with small size) per each image set.
- *generateIndividualBands*:  if `True`, it saves individual bands after performing all of the pre-processing.
- *overwrite*:  if `True`, it overwrites the pre-processed images (stacked, individual bands, and thumbnails) if there is an image with the same name in the corresponding folder.
- *envi_metadata*: it saves metadata with ENVI format for each multispectral (stacked) image.
- *pix4D_metadata*:  if `True`, it saves a CSV metadata for all individual bands. This information is required for processing the images (e.g., stitching the images) with Pix4D software.
- *save_json*: it extracts useful information (such as IMU and DLS data) from image metadata and saves them as a geojson file so we can open the captured images as points in QGIS/ArcGIS.
