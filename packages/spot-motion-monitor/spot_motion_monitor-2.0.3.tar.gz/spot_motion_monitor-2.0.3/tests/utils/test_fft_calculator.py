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
import pytest

from spot_motion_monitor.utils import fft_calculator

class TestFftCalculator:

    def test_calculation(self):
        np.random.seed(2000)
        L = 10
        x = np.random.normal(250.0, 1.0, L)
        y = np.random.normal(320.0, 1.0, L)
        fps = 2.0

        xFft, yFft, freqs = fft_calculator(x, y, fps)
        assert freqs.tolist() == pytest.approx([0.2, 0.4, 0.6, 0.8])
        assert xFft.tolist() == pytest.approx([3.98050167, -0.77153277, 3.03276981, -0.63908752])
        assert yFft.tolist() == pytest.approx([-1.28400998, -0.02015662, -0.03284222, -2.5690629])
