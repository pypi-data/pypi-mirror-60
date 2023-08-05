# This file is part of spot_motion_monitor.
#
# Developed for LSST System Integration, Test and Commissioning.
#
# See the LICENSE file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

from collections import namedtuple

__all__ = ['CameraStatus']

"""Camera related information

Attributes
----------
CameraStatus : collections.namedtuple
    Current values of particular camera information
    * name (str) : The name of the current camera.
    * currentFps (int) : The current Frames per Second rate.
    * isRoiMode (bool) : Flag for is the camera is acquiring Full or ROI frames.
    * frameOffset ((float, float)) : The current offset of the frame. Non-zero only in ROI mode.
    * showFrames (bool) : Flag for whether or not to show the CCD frames.
"""

CameraStatus = namedtuple('CameraStatus', 'name currentFps isRoiMode frameOffset showFrames')
