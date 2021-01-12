 
import numpy as np
import numpy.matlib as npm
import argparse
import json
import pprint
import exifread
import cv2 as cv
import os
import pywt
import math
import warnings
from scipy import ndimage
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from matplotlib import pyplot as plt
from os.path import basename

def noise_inconsistencies(file_path, block_size=8):


    img = cv.imread(file_path)
    img_rgb = img[:, :, ::-1]

    imgYCC = cv.cvtColor(img, cv.COLOR_BGR2YCrCb)
    y, _, _ = cv.split(imgYCC)

    coeffs = pywt.dwt2(y, 'db8')
    
    cA, (cH, cV, cD) = coeffs
    cD = cD[0:(len(cD)//block_size)*block_size,
            0:(len(cD[0])//block_size)*block_size]
    block = np.zeros(
        (len(cD)//block_size, len(cD[0])//block_size, block_size**2))
    

    for i in range(0, len(cD), block_size):
        for j in range(0, len(cD[0]), block_size):
            blockElement = cD[i:i+block_size, j:j+block_size]
            temp = np.reshape(blockElement, (1, 1, block_size**2))
            block[int((i-1)/(block_size+1)),
                  int((j-1)/(block_size+1)), :] = temp

    abs_map = np.absolute(block)
    med_map = np.median(abs_map, axis=2)
    noise_map = np.divide(med_map, 0.6745)
    
    print("Done")

    plt.subplot(1, 2, 1), plt.imshow(img_rgb), plt.title('Image')
    plt.xticks([]), plt.yticks([])
    plt.subplot(1, 2, 2), plt.imshow(noise_map), plt.title('Analysis')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Exposing digital forgeries by using Noise Inconsistencies')
    plt.show()
    
noise_inconsistencies('images/dog.jpeg')
