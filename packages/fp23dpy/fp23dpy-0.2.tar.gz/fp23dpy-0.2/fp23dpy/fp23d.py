"""
Module for 3D reconstructio of a fringe pattern image (the one you get from an FP-LIF setup)

The main method is fp23d which takes an image and an optional calibration as input and reconstructs 3D from it
"""
import numpy as np
from skimage import measure

from . import helpers as h
from . import Roi 
from . import demodulation as dd

def phase_to_threeD_const(T, theta, s=1):
    """
    Calculation of the proportionality constant between the threeD
    coordinates and the phase of a fringe pattern, assumes ortographic camera.

    :param T: Fringe pattern carrier period on a flat surface as seen with a camera with zero angle
    :param theta: Angle between camera direction to the fringe pattern projection direction in radians.
    :param s: The focal of the telecentric lens which corresponds to the length pixels/unit in the real world.
    :returns: Proportionality constant
    """
    return T / 2 / np.pi / np.sin(theta) / s

def threeD_to_phase_const(T, theta, s=1):
    """Simply the inverse of phase_to_threeD_const"""
    return 1 / phase_to_threeD_const(T, theta, s)


_min_percentile = 0.005
def fp23d(signal, calibration, negative_theta=False, same=False):
    """Function for 3D reconstruction of a fringe pattern, if no calibration has been performed the automated calibration fuction `fp23dpy.Calibration.calibrate` can be used"""
    signal = signal.astype(float)
    if np.ma.isMaskedArray(signal):
        mask = signal.mask
        roi = Roi.find_from_mask(mask)
        signal = roi.apply(signal)

    phase = dd.demodulate(signal, calibration)

    carrier = h.make_carrier(signal.shape[-2:], calibration['T'], calibration['gamma'])

    phase = (1 - 2 * negative_theta) * (phase - carrier)

    factor = 1.
    if 'theta' in calibration:
        factor *= phase_to_threeD_const(calibration['T'], calibration['theta'])
    if 'scale' in calibration:
        factor /= calibration['scale']
    if 'phi' in calibration:
        factor *= 1 / np.cos(np.abs(calibration['phi'] - calibration['gamma']))
    threeD = phase * factor

    if np.ma.isMaskedArray(threeD):
        if same:
            threeD = roi.unapply(threeD)
        mask = threeD.mask
        labels, n_labels = measure.label((~mask).astype(int), return_num=True)
        for j in range(1, n_labels + 1):
            valid = labels == j
            sum_valid = np.sum(valid)
            if sum_valid > 1000:
                threeD[valid] -= np.min(threeD[valid])
            else:
                print('Warning: too small segmented area of {} pixels removed'.format(sum_valid))
                mask[valid] = True
        threeD = np.ma.array(threeD.data, mask=mask, fill_value=0)
    else:
        points = np.sort(threeD.flatten())
        threeD -= points[int(round(_min_percentile * points.size))]
    return threeD
