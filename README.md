# Radiometric calibration of multispectral images
This repository offers a python-based batch processing pipeline for radiometric calibration of multispectral images captured by RedEdge imager. An appropriate radiometric calibration process has two main steps: (i) converting raw images to radiance (Wm-2sr-1nm-1) to account for sensor-dependent factors such as non-uniform spatial and spectral responses of the sensor in the camera (e.g., gain, offset, and quantum efficiency), (ii) converting radiance images to reflectance to account for variation in intensity of incident light over time [(reference)](https://www.frontiersin.org/articles/10.3389/fpls.2018.01182/full#h3).
My goal was to develop a batch processing pipeline for radiometric calibration of multispectral images with more functionality and flexibility, so I developed several python scripts and borrowed/modified several codes from [Micasense GitHub](https://github.com/micasense/imageprocessing) repository.


# Installation
I highly recommend visit [Micasense repository](https://github.com/micasense/imageprocessing) where you can find informative [tutorials](https://micasense.github.io/imageprocessing/index.html) and helpful information about the installation of the required packages.

To install the required packages, please refer to [Setup](https://micasense.github.io/imageprocessing/MicaSense%20Image%20Processing%20Setup.html) page and follow the instruction based on the operating system on your machine.
