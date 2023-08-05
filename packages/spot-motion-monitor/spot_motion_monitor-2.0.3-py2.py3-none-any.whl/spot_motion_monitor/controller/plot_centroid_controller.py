# This file is part of spot_motion_monitor.
#
# Developed for LSST System Integration, Test and Commissioning.
#
# See the LICENSE file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

from .. import config

__all__ = ['PlotCentroidController']

class PlotCentroidController():

    """This class handles the interactions between the main program and the
       1D centroid plots.

    Attributes
    ----------
    config : `config.CentroidPlotConfig`
        The instance that holds the current configuration.
    scatterPlot : .GraphicsLayoutWidget
        The scatter plot of the x,y pixel coordinate of the centroid.
    x1dPlot : .GraphicsLayoutWidget
        The 1D plot of the x pixel coordinate of the centroid.
    y1dPlot : .GraphicsLayoutWidget
        The 1D plot of the y pixel coordinate of the centroid.
    """

    def __init__(self, cxp, cyp, csp):
        """Initialize the class.

        Parameters
        ----------
        cxp : .GraphicsLayoutWidget
            The instance of the x centroid plot.
        cyp : .GraphicsLayoutWidget
            The instance of the y centroid plot.
        csp : .GraphicsLayoutWidget
            The instance of the centroid scatter plot.
        """
        self.x1dPlot = cxp
        self.y1dPlot = cyp
        self.scatterPlot = csp
        self.config = config.CentroidPlotConfig()

    def getPlotConfiguration(self):
        """Get the current camera configuration.

        Returns
        -------
        `config.CentroidPlotConfig`
            The set of current camera configuration parameters.
        """
        self.config.numHistogramBins = self.scatterPlot.getConfiguration()
        self.config.autoscaleX, ixrange, self.config.pixelRangeAdditionX = self.x1dPlot.getConfiguration()
        self.config.minimumX = ixrange[0]
        self.config.maximumX = ixrange[1]
        self.config.autoscaleY, iyrange, self.config.pixelRangeAdditionY = self.y1dPlot.getConfiguration()
        self.config.minimumY = iyrange[0]
        self.config.maximumY = iyrange[1]
        return self.config

    def setPlotConfiguration(self, config):
        """Set a new configuration on the Centroid plots.

        Parameters
        ----------
        config : `config.CentroidPlotConfig`
            The new configuration parameters.
        """
        self.x1dPlot.setConfiguration(config)
        self.y1dPlot.setConfiguration(config)
        self.scatterPlot.setConfiguration(config)

    def handleAcquireRoiStateChange(self, checked):
        """Deal with changes in the Acquire ROI checkbox.

        Parameters
        ----------
        checked : bool
            State of the Acquire ROI checkbox.
        """
        if not checked:
            self.x1dPlot.clearPlot()
            self.y1dPlot.clearPlot()
            self.scatterPlot.clearPlot()

    def setup(self, arraySize, roiFps):
        """Pass along the requested array size to the contained plot widgets.

        Parameters
        ----------
        arraySize : int
            The size for the plot data array.
        roiFps : float
            The current camera ROI frames per second.
        """
        self.x1dPlot.setup(arraySize, 'X', roiFps)
        self.y1dPlot.setup(arraySize, 'Y', roiFps)
        self.scatterPlot.setup(arraySize)

    def showScatterPlots(self, doShow):
        """Show the scatter plots.

        Parameters
        ----------
        doShow : bool
            True if plots are to be rendered, False if not.
        """
        if doShow:
            self.scatterPlot.showPlot()

    def update(self, cx, cy):
        """Update the x and y centroid plots and scatter plot data with current values.

        Parameters
        ----------
        cx : float
            The x pixel coordinate of the centroid.
        cy : float
            The y pixel coordinate of the centroid.
        """
        if cx is None or cy is None:
            return
        self.x1dPlot.updatePlot(cx)
        self.y1dPlot.updatePlot(cy)
        self.scatterPlot.updateData(cx, cy)

    def updateBufferSize(self, bufferSize):
        """Update the stored array sizes in the plot widgets.

        Parameters
        ----------
        bufferSize : int
            The new array size.
        """
        self.x1dPlot.setArraySize(bufferSize)
        self.y1dPlot.setArraySize(bufferSize)
        self.scatterPlot.setArraySize(bufferSize)

    def updateRoiFps(self, newRoiFps):
        """Update the stored ROI FPS in the plot widgets.

        Parameters
        ----------
        newRoiFps : int
            The new ROI FPS.
        """
        self.x1dPlot.setRoiFps(newRoiFps)
        self.y1dPlot.setRoiFps(newRoiFps)
