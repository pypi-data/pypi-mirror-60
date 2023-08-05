# This file is part of spot_motion_monitor.
#
# Developed for LSST System Integration, Test and Commissioning.
#
# See the LICENSE file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

names = ['Vimba', 'Gaussian']

from .base_camera import BaseCamera
from .camera_status import CameraStatus
from .gaussian_camera import GaussianCamera
try:
    from .vimba_camera import VimbaCamera
except AssertionError:
    pass
