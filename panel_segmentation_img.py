# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:18:35 2019

@author: coeadmin-amoghimi
"""

import numpy as np
import cv2
import skimage


# from skimage import morphology
panel_corners = []
#    area_threshold = 15000
area_threshold = 100

#    ratio_threshold = 0.95
ratio_threshold = 0.98
    
def panel_segmentation_img (panel):
    
    """ input is panel object from Panel class of micasense
        similar to Panel class of micasense"""

# ---------- setting the required thresholds ------------------------------
    
    img16 = panel.image.raw()
    
    img = (img16/256).astype('uint8')

    # ---------- thresholding - make it binary ------------------------------------

    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # ret3,bw = cv2.threshold(blur,0,255,cv2.THRESH_BINARY)
    #
#            cv2.imshow('img', bw)
#            cv2.waitKey(0)
#            cv2.destroyAllWindows()

    # ----------- labeling the objects in the binary image  -----------------------

    label_image = skimage.measure.label(bw, connectivity=2)

    # ----------- properties of the objects in the binary image  -----------------------

    props = skimage.measure.regionprops(label_image, intensity_image=None)

    #        axis_ratio = np.zeros((len(props),1))

    reference_panel_mask = np.zeros((bw.shape))

    for j in range(0, len(props)):

        # filtering small objects based on their area
        area_obj = props[j].area
        if area_obj < area_threshold:
            continue

        else:
            MajorAxisLength = props[j].major_axis_length
            MinorAxisLength = props[j].minor_axis_length
            axis_ratio_obj = MinorAxisLength / MajorAxisLength
            # masking objects based on the axis ratio - we know our panel is square
            if axis_ratio_obj >= ratio_threshold:
                reference_panel_mask[label_image == j + 1] = 255  # plus one because of background (it is zero)

    #
#               cv2.imshow('img', reference_panel_mask)
#               cv2.waitKey(0)
#               cv2.destroyAllWindows()

    temp_im = reference_panel_mask
    n_row, n_col = temp_im.shape

    area_rect = 0

    for i in range(n_row):
        for j in range(n_col):

            if temp_im[i, j] == 0:
                continue
            else:

                a = 1
                # move in rows
                while temp_im[i + a, j] == 255:
                    a = a + 1
                    #                temp_im[i+a, j] = 0
                    if a == 1:
                        continue
                a = a - 1
                b = 1
                # move in columns
                while temp_im[i, j + b] == 255:
                    b = b + 1
                    #                temp_im[i, j+b] = 0
                    if b == 1:
                        continue
                b = b - 1
                c = 1
                while temp_im[i + a, j + c] == 255:
                    c = c + 1
                c = c - 1
                if c < b:
                    width_rect = c
                else:
                    width_rect = b

                temp_area = (a + 1) * (width_rect + 1)

                if temp_area > area_rect:
                    area_rect = temp_area
                    i_top_left_corner = i
                    j_top_left_corner = j
                    height = a
                    width = width_rect


    top_left_corner = [j_top_left_corner, i_top_left_corner]
    top_right_corner = [j_top_left_corner+width, i_top_left_corner]
    bottom_right_corner = [j_top_left_corner+width, i_top_left_corner+height]
    bottom_left_corner = [j_top_left_corner, i_top_left_corner+height]

    panel_corners.append([top_left_corner, top_right_corner, bottom_right_corner, bottom_left_corner])
    
    return panel_corners