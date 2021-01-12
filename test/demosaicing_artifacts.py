
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
import progressbar
import warnings
from scipy import ndimage
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from matplotlib import pyplot as plt
from os.path import basename

def cfa_tamper_detection(file_path):
    print("Analyzing...")
    bar = progressbar.ProgressBar(maxval=20,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    warnings.filterwarnings("ignore")

    img = cv.imread(file_path)
    img = img[:, :, ::-1]

    std_thresh = 5
    depth = 3

    img = img[0:int(round(math.floor(img.shape[0]/(2**depth))*(2**depth))),
              0:int(round(math.floor(img.shape[1]/(2**depth))*(2**depth))), :]
    bar.update(5)

    small_cfa_list = np.asarray([[[2, 1], [3, 2]], [[2, 3], [1, 2]], [
                                [3, 2], [2, 1]], [[1, 2], [2, 3]]])

    # print(small_cfa_list)
    # print(small_cfa_list.shape)

    cfa_list = small_cfa_list

    # block size
    w1 = 16

    if img.shape[0] < w1 | img.shape[1] < w1:
        #f1_map = np.zeros((img.shape))
        #cfa_detected = [0, 0, 0, 0]
        return

    mean_error = np.ones((cfa_list.shape[0], 1))
    # print(mean_error.shape)
    bar.update(10)
    diffs = []
    f1_maps = []
    for i in range(cfa_list.shape[0]):

        bin_filter = np.zeros((img.shape[0], img.shape[1], 3))
        proc_im = np.zeros((img.shape[0], img.shape[1], 6))
        cfa = cfa_list[i]

        r = cfa == 1
        g = cfa == 2
        b = cfa == 3

        bin_filter[:, :, 0] = npm.repmat(
            r, img.shape[0]//2, img.shape[1]//2)
        bin_filter[:, :, 1] = npm.repmat(
            g, img.shape[0]//2, img.shape[1]//2)
        bin_filter[:, :, 2] = npm.repmat(
            b, img.shape[0]//2, img.shape[1]//2)

        cfa_im = np.multiply(1.0*img, bin_filter)

        bilin_im = bilinInterolation(cfa_im, bin_filter, cfa)
        # print(bilin_im[0:16,0:16,0])

        proc_im[:, :, 0:3] = img
        proc_im[:, :, 3:6] = 1.0*bilin_im
        proc_im = 1.0*proc_im
        # print(proc_im.shape)
        block_result = np.zeros(
            (proc_im.shape[0]//w1, proc_im.shape[1]//w1, 6))

        for h in range(0, proc_im.shape[0], w1):
            if h + w1 >= proc_im.shape[0]:
                break

            for k in range(0, proc_im.shape[1], w1):
                if k + w1 >= proc_im.shape[1]:
                    break
                out = eval_block(proc_im[h:h+w1, k:k+w1, :])
                block_result[h//w1, k//w1, :] = out

        stds = block_result[:, :, 3:6]
        block_diffs = block_result[:, :, 0:3]
        non_smooth = stds > std_thresh

        bdnm = block_diffs[non_smooth]
        mean_error[i] = np.average(np.reshape(bdnm, (1, bdnm.shape[0])))

        temp = np.sum(block_diffs, axis=2)
        rep_mat = np.zeros((temp.shape[0], temp.shape[1], 3))
        rep_mat[:, :, 0] = temp
        rep_mat[:, :, 1] = temp
        rep_mat[:, :, 2] = temp

        block_diffs = np.divide(block_diffs, rep_mat)

        # print(block_diffs.shape)

        diffs.append(np.reshape(
            block_diffs[:, :, 1], (1, block_diffs[:, :, 1].size)))

        f1_maps.append(block_diffs[:, :, 1])

    bar.update(15)

    diffs = np.asarray(diffs)
    diffs = np.reshape(diffs, (diffs.shape[0], diffs.shape[2]))

    for h in range(0, diffs.shape[0]):
        for k in range(0, diffs.shape[1]):
            if math.isnan(diffs[h, k]):
                diffs[h, k] = 0
    bar.update(18)
    f1_maps = np.asarray(f1_maps)
    val = np.argmin(mean_error)
    U = np.sum(np.absolute(diffs - 0.25), axis=0)
    U = np.reshape(U, (1, U.shape[0]))
    # print(U.shape)
    bar.update(19)
    #F1 = np.median(U)

    #CFADetected = cfa_list[val, :, :] == 2

    F1Map = f1_maps[val, :, :]
    bar.update(20)
    bar.finish()
    print("Done")

    plt.subplot(1, 2, 1), plt.imshow(img), plt.title('Image')
    plt.xticks([]), plt.yticks([])
    plt.subplot(1, 2, 2), plt.imshow(F1Map), plt.title('Analysis')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Image tamper detection based on demosaicing artifacts')
    plt.show()


def bilinInterolation(cfa_im, bin_filter, cfa):

    mask_min = np.divide(np.asarray([[1, 2, 1], [2, 4, 2], [1, 2, 1]]), 4.0)
    mask_maj = np.divide(np.asarray([[0, 1, 0], [1, 4, 1], [0, 1, 0]]), 4.0)

    if (np.argwhere(np.diff(cfa, axis=0) == 0).size != 0) | (np.argwhere(np.diff(cfa.T, axis=0) == 0).size != 0):
        mask_maj = np.multiply(mask_maj, 2.0)

    mask = np.ndarray(shape=(len(mask_min), len(mask_min[0]), 3))
    mask[:, :, 0] = mask_min[:, :]
    mask[:, :, 1] = mask_min[:, :]
    mask[:, :, 2] = mask_min[:, :]

    # print(mask)
    sum_bin_filter = np.reshape(
        np.sum(np.sum(bin_filter, axis=0), axis=0), (3))

    a = max(sum_bin_filter)
    # print(a)
    maj = np.argmax(sum_bin_filter)
    # print(maj)
    mask[:, :, maj] = mask_maj
    # print(mask)

    out_im = np.zeros((cfa_im.shape))

    for i in range(3):
        mixed_im = np.zeros((cfa_im.shape[0], cfa_im.shape[1]))
        orig_layer = cfa_im[:, :, i]
        #interp_layer = ndimage.convolve(orig_layer, mask[:,:,i])
        interp_layer = ndimage.correlate(
            orig_layer, mask[:, :, i], mode='constant')

        # print(interp_layer)

        for k in range(bin_filter.shape[0]):
            for h in range(bin_filter.shape[1]):
                if bin_filter[k, h, i] == 0:
                    mixed_im[k, h] = interp_layer[k, h]
                elif bin_filter[k, h, i] == 1:
                    mixed_im[k, h] = orig_layer[k, h]

        # print(mixed_im.shape)
        out_im[:, :, i] = mixed_im
        out_im = np.round(out_im)
        # print(out_im[:,:,0])
    return out_im

def eval_block(data):
    im = data

    Out = np.zeros((1, 1, 6))
    Out[:, :, 0] = np.mean(np.power(data[:, :, 0]-data[:, :, 3], 2.0))
    Out[:, :, 1] = np.mean(np.power(data[:, :, 1]-data[:, :, 4], 2.0))
    Out[:, :, 2] = np.mean(np.power(data[:, :, 2]-data[:, :, 5], 2.0))

    Out[:, :, 3] = np.std(np.reshape(im[:, :, 0], (1, im[:, :, 1].size)))
    Out[:, :, 4] = np.std(np.reshape(im[:, :, 1], (1, im[:, :, 2].size)))
    Out[:, :, 5] = np.std(np.reshape(im[:, :, 2], (1, im[:, :, 3].size)))

    # print(Out)
    return Out


image = 'images/cat.jpeg'
cfa_tamper_detection(image)