# This file is part of spot_motion_monitor.
#
# Developed for LSST System Integration, Test and Commissioning.
#
# See the LICENSE file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

import numpy as np
from scipy.fftpack import fft

__all__ = ['psd_calculator']

def psd_calculator(xVals, yVals, collectRate):
    """Calculate the power spectrum distribution for the centroid arrays.

    Parameters
    ----------
    xVals : numpy.array
        The x coordinates of the centroids.
    yVals : numpy.array
        The y coordinates of the centroids.
    collectRate : float
        The rate at which the data was collected (FPS).

    Returns
    -------
    (numpy.array, numpy.array, numpy.array)
        The PSDX, PSDY and Frequency arrays for the positive Frequency portion.
    """
    def make_psd(vals, dt):
        """Summary

        Parameters
        ----------
        vals : numpy.array
            The array of ROI centroid values.
        dt : float
            The inverse of the sampling rate.

        Returns
        -------
        numpy.array
            The calculated power spectrum distribution.
        """
        N = vals.size
        temp = np.abs(fft(vals))**2 * dt / N
        psd = temp[:N // 2]
        psd += temp[-1:-(N // 2) - 1:-1]
        return psd[1:]

    arrayLen = xVals.size
    deltaTime = 1 / collectRate

    psdX = make_psd(xVals, deltaTime)
    psdY = make_psd(yVals, deltaTime)

    deltaFrequency = collectRate / arrayLen
    frequencies = deltaFrequency * np.arange(arrayLen // 2)

    return psdX, psdY, frequencies[1:]
