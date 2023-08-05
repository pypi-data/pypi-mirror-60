.. include:: replacements.rst

.. _configuration:

=============
Configuration
=============

In addition to using the configuration menu from within the user interface, the
program provides a mechanism to insert configuration information into the program
on startup. The ``-c`` or ``--config_file`` flag may be passed to the ``smm_ui`` call.
The flag takes a filename corresponding to a YAML configuration file. The following sections
will describe the currently configurable parameters. Each section corresponds to a section
heading in the YAML configuration file.


general
~~~~~~~

This section handles modification to the program's general information and functionality. The following variables are configured under this section.

autorun
  A boolean parameter that allows the program to be started in ROI mode after launch. This parameter can also be set from the command line using the ``-a`` or ``--auto-run`` flag. If the configuration file is read in after program launch, this parameter has no effect.

configVersion
  A string that represents the version of the configuration file being used. The telemetry system places this information in a generated output configuration file. 

saveBufferData
  A boolean parameter that will allow one to automatically save the buffer data upon generation. See :ref:`this section<saveBufferData>` for more details on the generated files.

site
  A string that represents the location of the observations. There is no default site used within the program.

timezone
  A string containing the timezone to use for all date/times within the program. Default is ``UTC``. Supports ``TAI``. To specify other timezones, use the notation supported by the ``pytz`` module.

telemetry
---------

directory
  A string containing the path where the resulting telemetry data is to be stored. This parameter can be overridden from the command line using the ``-t`` or ``--telemetry_dir`` flag.

cleanup
^^^^^^^

directory
  A boolean parameter specifying if the telemetry directory is removed when ROI acquistion is stopped.
  
files
  A boolean parameter specifying if the telemetry files are removed when ROI acquisition is stopped. If ``directory`` is ``true``, setting this parameter to ``false`` has no effect. 

data
~~~~

This section handles modification to the program's data controller. The following variables are configured under this section.

buffer
------

pixelScale
  A decimal parameter that sets the sky scale on the camera CCD in units of arcseconds per pixel. This value will vary depending on the optical path in front of the CCD camera.

size
  An integer parameter that sets the size of the buffer to store the centroid data before performing calculations on a filled buffer. To make the power spectrum distribution calculations effective, the buffer size should be a power of 2 (|2^N|).

fullFrame
---------

minimumNumPixels
  An integer parameter that specifies the minimum number of pixels in the found object when calculating the center-of-masses within a CCD frame.

sigmaScale
  A decimal parameter that sets the scale factor for the standard deviation subtraction of a full CCD frame. The scale factor times the standard deviation is then subtracted from the frame.

roiFrame
--------

thresholdFactor
  A decimal parameter that specifies the scale factor for the maximum ADC value from a ROI CCD frame. The scale factor times the max ADC value is then subtracted from the frame.

camera
~~~~~~

full
----

fps
  An integer parameter that sets the frame rate (frames per second) for CCD full frame acquisition. Note: The Gaussian camera does not support frame rates over 40 due to the Poisson background generation. For a Vimba camera, consult the appropriate documentation to find the supported range. 

exposureTime
  This attribute only applies to Vimba cameras. An integer parameter giving the exposure time of the camera when using full frame mode in units of |microseconds|.

roi
---

fps
  An integer parameter that sets the frame rate (frames per second) for CCD ROI frame acquisition. Note: The Gaussian camera does not support frame rates over 40 due to the frame generation methodology. For a Vimba camera, consult the appropriate documentation to find the supported range. The program has been tested to work with Vimba camera frame rates up to 120 before the CCD plot feature needs to be switched off in order to obtain higher frame rates.

size
  An integer parameter that sets the size of the ROI region in pixels. By the nature of the program, the ROI region is fixed to be a square.

exposureTime
  This attribute only applies to Vimba cameras. An integer parameter giving the exposure time of the camera when using ROI frame mode in units of |microseconds|.

fluxMin
  This attribute only applies to Vimba cameras. An integer parameter setting the minimum ADC sum of the ROI for a given frame. Frames lower than this minimum are rejected.

spotOscillation
---------------

This section only applies to a Gaussian camera.

do
^^
  A boolean parameter that determines if the sport oscillation is executed.

x
^

amplitude
  An integer parameter that specifies the amplitude of the oscillation in the x direction. Parameter units are pixels.

frequency
  A decimal parameter that sets the frequency of the oscillation in the x direction. Parameter units are Hz.

y
^

amplitude
  An integer parameter that specifies the amplitude of the oscillation in the y direction. Parameter units are pixels.

frequency
  A decimal parameter that sets the frequency of the oscillation in the y direction. Parameter units are Hz.

plot
~~~~

This section contains the parameters for the various plots in the program. The only plot that is not configurable via this file is the CCD frame plot.

centroid
--------

This section contains the parameters for the three different centroid plots: scatter, 1D x and y.

scatterPlot
^^^^^^^^^^^

This section contains parameters associated with the scatter plot.

histograms
++++++++++

This section contains parameters associated with the scatter plot projection histograms.

numBins
  An integer parameter that sets the number of bins for each of the projection histograms.

xCentroid
^^^^^^^^^

This section contains parameters for the 1D x centroid plot.

autoscaleY
  An enumerated string parameter that sets the scaling for the y axis. The potential values are:

  * ON - Autoscaling is applied.
  * PARTIAL - Plot is autoscaled for first 15 frames, then a minimum and maximum are calculated from the captured values and set on the plot.
  * OFF - No autoscaling applied. Minimum and maximum values need to be set for the plot.

minimumY
  A decimal parameter that controls the minimum value for the y axis. Only applies when ``autoscaleY`` is in ``OFF`` mode.

maximumY
  A decimal parameter that controls the maximum value for the y axis. Only applies when ``autoscaleY`` is in ``OFF`` mode.

pixelRangeAddition
  An integer parameter to add to the quick average of the centroid values when using ``autoscaleY`` in ``PARTIAL`` mode. This sets the minimum and maximum value for the plot.

yCentroid
^^^^^^^^^

This section contains parameters for the 1D y centroid plot.

autoscaleY
  An enumerated string parameter that sets the scaling for the y axis. The potential values are:

  * ON - Autoscaling is applied.
  * PARTIAL - Plot is autoscaled for first 15 frames, then a minimum and maximum are calculated from the captured values and set on the plot.
  * OFF - No autoscaling applied. Minimum and maximum values need to be set for the plot.

minimumY
  A decimal parameter that controls the minimum value for the y axis. Only applies when ``autoscaleY`` is in ``OFF`` mode.

maximumY
  A decimal parameter that controls the maximum value for the y axis. Only applies when ``autoscaleY`` is in ``OFF`` mode.

pixelRangeAddition
  An integer parameter to add to the quick average of the centroid values when using ``autoscaleY`` in ``PARTIAL`` mode. This sets the minimum and maximum value for the plot.

psd
---

This section contains the parameters for the four different power spectrum distribution plots: Waterfall x and y, 1D x and y.

waterfall
^^^^^^^^^

This section contains parameters for the x and y waterfall plots.

colormap
  A string parameter that sets the color map for the waterfall plot. The currently supported options are:

  * viridis
  * plasma
  * inferno
  * magma
  * cividis

numBins
  An integer parameter that controls the number of bins (N) kept in the vertical direction on the plot. This sets the hold time (H) of the data based on the current buffer accumulation time (T) as H = N x T

xPSD
^^^^

This section contains parameters for the 1D x power spectrum distribution plot.

autoscaleY
  A boolean parameter that controls the automatic scaling of the y axis.

maximumY
  A decimal parameter that controls the maximum value of the y axis. This does not need to be set if ``autoscaleY`` is ``false``.

yPSD
^^^^

This section contains parameters for the 1D y power spectrum distribution plot.

autoscaleY
  A boolean parameter that controls the automatic scaling of the y axis.

maximumY
  A decimal parameter that controls the maximum value of the y axis. This does not need to be set if ``autoscaleY`` is ``false``.


Full Example
~~~~~~~~~~~~

This section will show a full example of all items that are configurable based on a configuration saved from the program. The ``camera`` section is for the Gaussian camera. The file passed to the program does not need to contain all of the sections and variables that are shown here.

::

  camera:
    full:
      fps: 24
    roi:
      fps: 40
      size: 50
    spotOscillation:
      do: true
      x:
        amplitude: 10
        frequency: 1.0
      y:
        amplitude: 5
        frequency: 2.0
  data:
    buffer:
      pixelScale: 1.0
      size: 1024
    fullFrame:
      minimumNumPixels: 10
      sigmaScale: 5.0
    roiFrame:
      thresholdFactor: 0.3
  general:
    autorun: false
    configVersion: "1.0.1"
    saveBufferData: false
    site: null
    telemetry:
      cleanup:
        directory: true
        files: true
      directory: null
    timezone: UTC
  plot:
    centroid:
      scatterPlot:
        histograms:
          numBins: 40
      xCentroid:
        autoscaleY: PARTIAL
        maximumY: null
        minimumY: null
        pixelRangeAddition: 10
      yCentroid:
        autoscaleY: PARTIAL
        maximumY: null
        minimumY: null
        pixelRangeAddition: 10
    psd:
      waterfall:
        colorMap: viridis
        numBins: 25
      xPSD:
        autoscaleY: true
        maximumY: null
      yPSD:
        autoscaleY: true
        maximumY: null

The following shows the camera section of a Vimba camera configuration.

::

  camera:
    full:
      exposureTime: 8000
      fps: 24
    roi:
      exposureTime: 8000
      fluxMin: 2000
      fps: 40
      size: 50
