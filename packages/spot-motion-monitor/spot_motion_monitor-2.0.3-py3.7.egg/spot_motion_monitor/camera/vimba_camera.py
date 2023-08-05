# This file is part of spot_motion_monitor.
#
# Developed for LSST System Integration, Test and Commissioning.
#
# See the LICENSE file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

from collections import OrderedDict
import time

import numpy as np
import pymba as pv

from spot_motion_monitor.camera import BaseCamera
from ..config import VimbaCameraConfig
from spot_motion_monitor.utils import CameraNotFound, FrameCaptureFailed, getTimestamp

__all__ = ['VimbaCamera']

class VimbaCamera(BaseCamera):

    """This class handles the connection to an Allied Vision camera through
       the Vimba interface.

    Attributes
    ----------
    badFrames : int
        Counter for the number of failed frame captures.
    cameraIndex : int
        Requested index in list of camera.
    cameraPtr : pymba.VimbaCamera
        Instance of the actual camera object.
    config : `config.VimbaCameraConfig`
        Instance of the camera configuration.
    fluxMinRoi : int
        The minimum flux allowed for an ROI frame.
    fpsFullFrame : int
        The Frames per Second rate in full frame mode.
    fpsRoiFrame : int
        The Frames per Second rate in ROI frame mode.
    frame : pymba.VimbaFrame
        Instance of the frame object for the camera.
    frameShape : tuple(int, int)
        Describe the shape of the frame being converted.
    goodFrames : int
        Counter for the number of capture frames.
    height : int
        The pixel height of the CCD.
    image : numpy.array
        The current converted CCD frame.
    isRoiMode : bool
        Whether or not the camera is in ROI mode.
    offsetX : int
        The current offset in X for the camera.
    offsetY : int
        The current offset in Y for the camera.
    roiExposureTime : int
        The camera exposure time (microseconds) in ROI mode.
    roiSize : int
        The size of a (square) ROI region in pixels.
    STREAM_BYTES_PER_SECOND : int
        The maximum value for a GigE interface.
    totalFrames : int
        Counter for the total number of requested frames.
    vimba : pymba.Vimba
        Instance of the Python control library.
    width : int
        The pixel width of the CCD.
    """

    def __init__(self):
        """Initalize the class.
        """
        super().__init__()
        self.vimba = None
        self.cameraIndex = 0
        self.cameraPtr = None
        self.frame = None
        self.fpsFullFrame = 24
        self.fpsRoiFrame = 40
        self.roiSize = 50
        self.roiExposureTime = 8000  # microseconds
        self.fullExposureTime = 8000  # microseconds
        self.fluxMinRoi = 2000
        self.offsetX = 0
        self.offsetY = 0
        self.image = None
        self.frameShape = None
        self.isRoiMode = False
        self.config = VimbaCameraConfig()

        self.STREAM_BYTES_PER_SECOND = 124000000

    @property
    def modelName(self):
        """Return the camera model name.

        Returns
        -------
        str
            The camera model name.
        """
        if self.cameraPtr is not None:
            temp = [self.cameraPtr.DeviceVendorName, self.cameraPtr.DeviceModelName]
            return ' '.join(temp)
        else:
            return 'Camera Stopped'

    def checkFullFrame(self, flux, maxAdc, comX, comY):
        """Use the provided quantities to check frame validity.

        Parameters
        ----------
        flux : float
            The flux of the frame.
        maxAdc : float
            The maximum ADC of the frame.
        comX : float
            The x component of the center-of-mass.
        comY : float
            The y component of the center-of-mass.

        Returns
        -------
        bool
            True if frame is valid, False if not.
        """
        return flux > 100 and maxAdc > 0 and comX > 0 and comY > 0

    def checkRoiFrame(self, flux):
        """Use the provided quantities to check frame validity

        Parameters
        ----------
        flux : float
            The flux of the frame.

        Returns
        -------
        bool
            True if frame is valid, False if not.
        """
        return flux > self.fluxMinRoi

    def convertFrame(self, frame):
        """Convert frame into numpy array.

        Parameters
        ----------
        frame: `pymba.Frame`
            The current frame from the camera to convert.

        Raises
        ------
        FrameCaptureFailed
            Raises this if conversion of frame fails.
        """
        try:
            frameData = frame.buffer_data()
            self.image = np.ndarray(buffer=frameData, dtype=np.uint16, shape=self.frameShape)
        except pv.VimbaException:
            raise FrameCaptureFailed(f"{getTimestamp()} Frame conversion failed.")

    def getCameraInformation(self):
        """Return the current camera related information.

        Returns
        -------
        OrderedDict
            The set of camera information.
        """
        info = OrderedDict()
        info['Vendor'] = self.cameraPtr.DeviceVendorName
        info['Model'] = self.cameraPtr.DeviceModelName
        info['Part Number'] = self.cameraPtr.DevicePartNumber
        info['Firmware Version'] = self.cameraPtr.DeviceFirmwareVersion
        info['CCD Width (pixels)'] = self.width
        info['CCD Height (pixels)'] = self.height
        info['Pixel Format'] = self.cameraPtr.PixelFormat
        info['Gain Auto'] = self.cameraPtr.GainAuto
        info['Exposure Auto'] = self.cameraPtr.ExposureAuto

        return info

    def getConfiguration(self):
        """Get the current camera configuration.

        Returns
        -------
        `config.VimbaCameraConfig`
            The set of current configuration parameters.
        """
        self.config.roiSize = self.roiSize
        self.config.fpsRoiFrame = self.fpsRoiFrame
        self.config.fpsFullFrame = self.fpsFullFrame
        self.config.roiFluxMinimum = self.fluxMinRoi
        self.config.roiExposureTime = self.roiExposureTime
        self.config.fullExposureTime = self.fullExposureTime
        return self.config

    def getFullFrame(self):
        """Get the full frame from the CCD.

        Returns
        -------
        numpy.array
            The current full CCD frame.

        Raises
        ------
        FrameCaptureFailed
            Raises this if the camera fails to capture the frame when
            requested.
        """
        if self.isRoiMode:
            self.isRoiMode = False
            self.frameShape = (self.height, self.width)

        try:
            self.cameraPtr.start_frame_acquisition()
        except pv.VimbaException as err:
            raise FrameCaptureFailed("{} Full frame capture failed: {}".format(getTimestamp(), str(err)))

        return self.image

    def getOffset(self):
        """Get the offset for the CCD frame.

        Returns
        -------
        (int, int)
            The current offset of the CCD frame.
        """
        return (self.offsetX, self.offsetY)

    def getRoiFrame(self):
        """Get the ROI frame from the CCD.

        Returns
        -------
        numpy.array
            The current ROI CCD frame.

        Raises
        ------
        FrameCaptureFailed
            Raises this if the camera fails to capture the frame when
            requested.
        """
        if not self.isRoiMode:
            self.isRoiMode = True
            self.frameShape = (self.roiSize, self.roiSize)

        self.totalFrames += 1
        try:
            self.cameraPtr.start_frame_acquisition()
            self.goodFrames += 1
        except pv.VimbaException as err:
            self.badFrames += 1
            raise FrameCaptureFailed("{} ROI frame capture failed: {}".format(getTimestamp(), str(err)))

        self.cameraPtr.stop_frame_acquisition()

        return self.image

    def resetOffset(self):
        """Reset the camera offsets back to zero.
        """
        self.cameraPtr.OffsetX = 0
        self.cameraPtr.OffsetY = 0
        self.offsetX = 0
        self.offsetY = 0
        self.cameraPtr.Height = self.height
        self.cameraPtr.Width = self.width

    def setConfiguration(self, config):
        """Set the comfiguration on the camera.

        Parameters
        ----------
        config : `config.VimbaCameraConfig`
            The current configuration.
        """
        self.cameraIndex = config.cameraIndex
        self.roiSize = config.roiSize
        self.fpsRoiFrame = config.fpsRoiFrame
        self.fpsFullFrame = config.fpsFullFrame
        self.fluxMinRoi = config.roiFluxMinimum
        self.roiExposureTime = config.roiExposureTime
        self.fullExposureTime = config.fullExposureTime
        if self.cameraPtr is not None:
            self.cameraPtr.ExposureTimeAbs = self.roiExposureTime

    def showFrameStatus(self):
        """Show frame status from the camera.

        The camera reports the number of good, bad and total frames to the
        system.
        """
        if self.badFrames:
            print("{} {}, {}, {}".format(getTimestamp(), self.goodFrames, self.badFrames, self.totalFrames))

    def startup(self):
        """Handle the startup of the camera.

        Raises
        ------
        CameraNotFound
            Raises this exception if there is an issue with the camera.
        """
        self.goodFrames = 0
        self.badFrames = 0
        self.totalFrames = 0
        self.vimba = pv.Vimba()
        self.vimba.startup()
        time.sleep(0.2)
        cameraIds = self.vimba.camera_ids()
        try:
            self.cameraPtr = self.vimba.camera(cameraIds[self.cameraIndex])
        except IndexError:
            raise CameraNotFound('Camera not found ... check power or connection!')

        self.cameraPtr.open()
        #self.cameraPtr.GevSCPSPacketSize = 1500
        try:
            currentSbps = self.cameraPtr.StreamBytesPerSecond
            self.cameraPtr.StreamBytesPerSecond = self.STREAM_BYTES_PER_SECOND
        except pv.VimbaException:
            message = f'Issue with ethernet cable ... StreamBytesPerSecond: {currentSbps}'
            message += f' instead of {self.STREAM_BYTES_PER_SECOND}'
            raise CameraNotFound(message)
        self.height = self.cameraPtr.HeightMax
        self.width = self.cameraPtr.WidthMax
        self.frameShape = (self.height, self.width)
        self.cameraPtr.Height = self.height
        self.cameraPtr.Width = self.width
        self.cameraPtr.OffsetX = 0
        self.cameraPtr.OffsetY = 0
        self.cameraPtr.GainAuto = 'Off'
        self.cameraPtr.GainRaw = 0
        self.cameraPtr.ExposureAuto = 'Off'
        self.cameraPtr.TriggerSource = 'Freerun'
        self.cameraPtr.PixelFormat = 'Mono12'
        self.cameraPtr.ExposureTimeAbs = self.roiExposureTime

        self.cameraPtr.arm('Continuous', self.convertFrame)

    def shutdown(self):
        """Handle the shutdown of the camera.
        """
        if self.vimba is None:
            return
        if self.cameraPtr is not None:
            try:
                self.cameraPtr.disarm()
                self.cameraPtr.close()
            except pv.VimbaException:
                pass
            except FrameCaptureFailed:
                pass
        self.vimba.shutdown()
        self.cameraPtr = None
        self.image = None

    def updateOffset(self, centroidX, centroidY):
        """Update the camera's internal offset values from the provided centroid.

        For the Gaussian camera, this is a no-op, but helps test the mechanism.

        Parameters
        ----------
        centroidX : float
            The x component of the centroid for offset update.
        centroidY : float
            The y component of the centroid for offset update.
        """
        self.offsetX = int(centroidX - self.roiSize / 2)
        self.offsetY = int(centroidY - self.roiSize / 2)
        self.cameraPtr.OffsetX = self.offsetX
        self.cameraPtr.OffsetY = self.offsetY
        self.cameraPtr.Height = self.roiSize
        self.cameraPtr.Width = self.roiSize

    def waitOnRoi(self):
        """Wait on information to be updated for ROI mode use.

        Run the loop until both the reported camera height and width are the
        same size as the specified ROI.
        """
        while True:
            if self.cameraPtr.Height == self.roiSize and self.cameraPtr.Width == self.roiSize:
                break
