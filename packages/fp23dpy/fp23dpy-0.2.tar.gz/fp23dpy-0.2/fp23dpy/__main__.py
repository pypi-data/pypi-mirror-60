"""
Main script for 3D reconstruction of Fringe Pattern images
"""
import argparse
import numpy as np
import os
import os.path as osp
from skimage import io
try:
    from tqdm import tqdm
except:
    tqdm = lambda x: x

from . import Calibration
from . import Roi
from . import fp23d 
from . import helpers as h
from . import file3DPrinter as f3p


### Quick fix of calibration ###
import sys
if 'calibrate' in sys.argv:
    sys.argv.remove('calibrate')
    from . import __calibrate_main__; __calibrate_main__
    exit()


parser = argparse.ArgumentParser(description='3D reconstruct images with Fringe Patterns')
parser.add_argument('files', type=str, nargs='+',
                    help='Input image files to reconstruct, files with prefix "reconstructed" and "segmented" will not be considered')
parser.add_argument('--output', '-o', type=str,
                    help='Output directory for the reconstructed 3D files, default is the same as input files')
parser.add_argument('--prefix', type=str, default='reconstructed_',
                    help='Prefix of the reconstructed 3D files, default is "reconstructed_"')
parser.add_argument('--ext', type=str, default='obj',
                    help='Output 3D file format, default is wavefront .obj')
# parser.add_argument('--ransac', action='store_true',
#                     help='Use ransac to estimate a quadratic background carrier (currently not implemented).')
parser.add_argument('--negative_theta', action='store_true',
                    help='If the camera is above or to the right of the projector this option should be used or a negative theta should be set in calibration file.')
parser.add_argument('--same', action='store_true',
                    help='Do not crop the output results.')
parser.add_argument('--print-image', action='store_true',
                    help='Print the reconstruction as an image filed scaled for simple visualisation of the result, the pixel values will only correspond to relative reconstruction.')
parser.add_argument('--print-ascii', action='store_true',
                    help='Print the reconstruction as an ascii text file for later import into python.')
parser.add_argument('--print-roi', action='store_true',
                    help='Print the rectangle of interest used for the output images.')
parser.add_argument('--roi-file', type=str, default='roi.txt',
                    help='The name for the roi file, default is "roi.txt"')
args = parser.parse_args()
method_args = ['negative_theta', 'same']
d_args = {key: vars(args)[key] for key in method_args}

output_image_type = np.uint8

###### Manipulating input files ######
to_reconstruct = args.files
if osp.isdir(to_reconstruct[0]):
    input_dir = to_reconstruct[0]
    to_reconstruct = [f for f in os.listdir(input_dir) if h.is_image_file(f)]
else:
    input_dir = osp.dirname(to_reconstruct[0])

if len(to_reconstruct) > 0:
    to_reconstruct = [f for f in to_reconstruct if not 'calibrat' in f and not 'segment' in f and not 'reconstruct' in f]
if len(to_reconstruct) == 0:
    print("No images found to reconstruct")
    exit()
to_reconstruct = sorted(to_reconstruct)

global_calibration = None
global_calibration_file = osp.join(input_dir, 'calibration.txt')
if osp.isfile(global_calibration_file):
    global_calibration = Calibration.read(global_calibration_file)

global_mask = None
global_roi = Roi()
global_segmentation_file_png = osp.join(input_dir, 'segmentation.png')
global_segmentation_file_tif = osp.join(input_dir, 'segmentation.tif')
if osp.isfile(global_segmentation_file_png):
    segmented = io.imread(global_segmentation_file_png, as_gray=True)
    global_mask = segmented == 0
    global_roi = Roi.find_from_mask(global_mask)
elif osp.isfile(global_segmentation_file_tif):
    segmented = io.imread(global_segmentation_file_tif, as_gray=True)
    global_mask = segmented == 0
    global_roi = Roi.find_from_mask(global_mask)

max_roi = Roi()

###### Demodulation of files ######
if len(to_reconstruct) == 1:
    tqdm = lambda x: x
reconstructed = []
for input_file in tqdm(to_reconstruct):
    input_dir, input_file_name = osp.split(input_file)
    input_file_name_base, _ = osp.splitext(input_file_name)
    if not osp.isfile(input_file):
        print("Warning: File {} not found".format(input_file))
        continue

    signal = io.imread(input_file, as_gray=True)

    local_calibration_file = osp.join(input_dir, 'calibration_' + input_file_name_base + '.txt')
    if osp.isfile(local_calibration_file):
        calibration = Calibration.read(local_calibration_file)
    elif not global_calibration is None:
        calibration = global_calibration
    else:
        print("Warning: No calibration file found, using automatic calibration algorithm") 
        calibration = Calibration.calibrate(signal)
        print(calibration)

    local_segmentation_file = osp.join(input_dir, 'segmented_' + input_file_name)
    if osp.isfile(local_segmentation_file):
        segmented = io.imread(local_segmentation_file, as_gray=True)
        mask = segmented == 0
        signal = np.ma.array(signal, mask=mask, fill_value=0)
        roi = Roi.find_from_mask(mask)
    elif not global_mask is None:
        signal = np.ma.array(signal, mask=global_mask, fill_value=0)
        roi = global_roi
    else:
        roi = Roi.full(signal.shape)
    if args.same:
        roi = Roi.full(signal.shape)

    texture_file = osp.join(input_dir, input_file_name_base + '_texture.png')
    texture = None
    if osp.isfile(texture_file):
        texture = io.imread(texture_file)
        texture = roi.apply(texture)


    threeD = fp23d(signal, calibration, **d_args)
    reconstructed += [(input_file, threeD, texture, calibration, roi)]

    if max_roi.empty() or list(signal.shape) == max_roi.full_shape():
        max_roi.maximize(roi)

    # plt.subplot(121)
    # plt.imshow(signal)
    # plt.subplot(122)
    # plt.imshow(threeD)
    # plt.show()


###### Post processing of 3D files ######
if len(reconstructed) == 0:
    print("No files were reconstructed")
    exit()
if len(to_reconstruct) > 1:
    print('Working on 3D files')

if args.print_roi:
    max_roi.write(osp.join(input_dir, args.roi_file))
roi = reconstructed[0][4].copy()
roi.rebase(max_roi)

base_threeD = roi.unapply(reconstructed[0][1])
for (input_file, threeD, texture, calibration, roi) in tqdm(reconstructed):
    xscale = yscale = 1
    if 'theta' in calibration:
        xscale *= 1 / np.cos(calibration['theta'])
    if 'phi' in calibration:
        phi = calibration['phi']
        factor = xscale - 1
        xscale = 1 + np.cos(phi) * xscale
        yscale = 1 + np.sin(phi) * xscale
    if 'scale' in calibration:
        xscale /= calibration['scale']
        yscale /= calibration['scale']

    if roi.full_shape() == max_roi.full_shape():
        roi.rebase(max_roi)
        threeD = roi.unapply(threeD)
        diff = threeD - base_threeD
        if np.ma.isMaskedArray(threeD):
            diff = diff[diff.mask == False].data
        l = np.median(diff)
        threeD -= l
        base_threeD = threeD

    
    input_dir, input_file_name = osp.split(input_file)
    output_dir = input_dir if args.output is None else args.output
    input_file_name_base = osp.splitext(input_file_name)[0]
    f3p.print_it(osp.join(output_dir, '{}{}.{}'.format(args.prefix, input_file_name_base, args.ext)), threeD, texture, xscale=xscale, yscale=yscale)

    if np.ma.isMaskedArray(threeD):
        threeD.data[threeD.mask] = 0
        threeD.fill_value = 0

    if args.print_ascii:
        np.savetxt(osp.join(output_dir, '{}{}.csv'.format(args.prefix, input_file_name_base)), threeD, fmt='%.3f')

    if args.print_image:
        threeD = h.image_scaled(threeD, (0, np.iinfo(output_image_type).max))
        output_file = osp.join(output_dir, '{}{}'.format(args.prefix, input_file_name))
        io.imsave(output_file, threeD.astype(output_image_type))
