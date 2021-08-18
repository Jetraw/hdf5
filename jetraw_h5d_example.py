# -*- coding: utf-8 -*-
import os
import pathlib
import h5py
import dpcore
import numpy as np
import ctypes.util
from PIL import Image

h5py._errors.unsilence_errors()

# 1. OPEN HDF5 IMAGE
# load uncompressed dataset
baseFolder = pathlib.Path("/home/user/images/")
inputFile = "test_hdf5.h5"

inputHDF5 = h5py.File(baseFolder.joinpath(inputFile), "r+")
# retrieve HDF5 dataset from specific dataset
h5Dataset = inputHDF5["/t0/channel0"]

# 2. PREPARE image usign dpcore
image = np.array(h5Dataset[:])
# NOTE: with noise filter ON 61003908_4_95000000_1 (PCO Edge 4.2)
cameraId = "61003908_4_95000000_0"
imageShape = h5Dataset.shape
for idx in range(imageShape[0]):
    # get ctype pointer to image page
    imagePtr = image[idx, :, :].ctypes.data_as(ctypes.POINTER(ctypes.c_ushort))
    # call dpcore to prepare image page
    status = dpcore._dpcore_lib.dpcore_prepare_image(imagePtr, imageShape[1] * imageShape[2], cameraId.encode('utf-8'), 1.0)
    # verify dpcore prepare image status
    if status != 0:
        raise RuntimeError("Dpcore prepare image error with status " + status)

# This will remove outfile if it already exists
outputFile = "output.p.h5"
if os.access(baseFolder.joinpath(outputFile), os.F_OK):
    os.remove(baseFolder.joinpath(outputFile))

# 3. COMPRESS
try:
    outputHDF5 = h5py.File(baseFolder.joinpath(outputFile), "a")
    # set chunk size to the same as input (not used at the moment)
    chunks = h5Dataset.chunks

    # lossless jetraw compression
    jetrawH5Dataset = outputHDF5.create_dataset("jetraw", data=image[:], chunks=imageShape, compression=32100,
                                                compression_opts=(imageShape[0], imageShape[1], imageShape[2]))
    outputHDF5.close()
except Exception as exception:
    print("[ERROR] create_dataset HDF5 dataset error : " + str(exception))

# 4. TEST RESULT
# open compressed jetraw to verify results
try:
    jetrawInputFile = h5py.File(baseFolder.joinpath(outputFile), "r+")
    jetrawH5Dataset = jetrawInputFile['jetraw']
except Exception as exception:
    print("[ERROR] file HDF5 read dataset error : " + str(exception))

# save last page of image
imageToSave = Image.fromarray(jetrawH5Dataset[imageShape[0] - 1, :, :])
imageToSave.save(baseFolder.joinpath("jetraw_hdf5_image.png"))
