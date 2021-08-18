# HDF5 Jetraw

The HDF5 module for Jetraw. You can use Dotphoton's Jetraw compression with your HDF5 files integrating this 
filter in your HDF5 workflow. 

For more info visit our website:
www.jetraw.com 

## Requirements

- Windows 10 64 bits or Linux
- Jetraw and Dpcore installed and running in your system. Also included in the system PATH.
- Python 3.7+ and h5py 3.2.0+
- HDF5 1.8.11+

## Install Windows

Copy the HDF5 Jetraw filter (h5jetrawfilter.dll) into your HDF5 install plugin path (e.g. path_to_HDF_installation\HDF5\1.8.18\lib\plugin\)

## Install Linux

Copy the HDF5 Jetraw filter (libh5jetrawfilter.so) into your desired folder and export the environment variable HDF5_PLUGIN_PATH to the chosen folder:

```
export HDF5_PLUGIN_PATH=/desired_folder_for_hdf5_filters/
```

You also need to add to the LD_LIBRARY_PATH variable to the dpcore and jetraw libraries location so the HDF5 filter is able to find them:

```
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/path_to_jetraw_folder/lib/
```

You can simply **add those two instructions in your bashrc (/home/user/.bashrc)** file, then everytime a bash environment is created everything is set up to use the HDF5 filter. 

## Usage

We will follow the example provided in this git repository to read an HDF5 file, prepare it with dpcore and compress it with Jetraw. 

```python
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
baseFolder = "path_to_images"
inputFile  = "image.h5"

inputHDF5 = h5py.File(baseFolder + inputFile, "r+")
# retrieve HDF5 dataset from specific group
h5Dataset = inputHDF5['group_name']


# 2. PREPARE (dpcore)
# prepare image with dpcore
image = np.array(h5Dataset[:])
cameraId = "camera_id_example"
imageShape = h5Dataset.shape
for idx in range(imageShape[0]):
    # get ctype pointer to image page
    imagePtr = image[idx, :, :].ctypes.data_as(ctypes.POINTER(ctypes.c_ushort))
    # call dpcore to prepare image page
    status = dpcore._dpcore_lib.dpcore_prepare_image(imagePtr, imageShape[1]*imageShape[2], cameraId.encode('utf-8') , 1.0)
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

```

If you want to **visualize a compressed image using Fiji**, you can simply use the build-in plug-in HDF5. Remember that you will need to **launch your Fiji** 
**app from the Terminal** as the HDF5_PLUGIN_PATH environment variable needs to be properly loaded, if not HDF5 will not find the jetraw filter to decompress 
the image. 

## Contact
Feel free to use the [issues section](https://github.com/Jetraw/hdf5/issues) to report bugs or request new features. You can also ask questions and give comments by visiting the [discussions](https://github.com/Jetraw/hdf5/discussions), or following the contact information at https://jetraw.com.