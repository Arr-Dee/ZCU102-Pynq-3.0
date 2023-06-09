#   Copyright (c) 2018, Xilinx, Inc.
#   SPDX-License-Identifier: BSD-3-Clause


import warnings

from pynq import DefaultHierarchy
from pynq.ps import CPU_ARCH, ZYNQ_ARCH
from .common import *
from .frontend import VideoInFrontend, VideoOutFrontend


class HDMIInFrontend(VideoInFrontend, DefaultHierarchy):
    """Class for interacting the with HDMI input frontend

    This class is used for enabling the HDMI input and retrieving
    the mode of the incoming video

    Attributes
    ----------
    mode : VideoMode
        The detected mode of the incoming video stream

    """

    def __init__(self, description):
        super().__init__(description)

    def start(self, init_timeout=60):
        """Method that blocks until the video mode is
        successfully detected

        """
        import pynq.lib._video

        ip_dict = self.description
        gpio_description = ip_dict["ip"]["axi_gpio_hdmiin"]
        gpio_dict = {
            "BASEADDR": gpio_description["phys_addr"],
            "INTERRUPT_PRESENT": 1,
            "IS_DUAL": 1,
        }
        vtc_description = ip_dict["ip"]["vtc_in"]
        vtc_capture_addr = vtc_description["phys_addr"]
        self._capture = pynq.lib._video._capture(
            gpio_dict, vtc_capture_addr, init_timeout
        )

    def stop(self):
        """Currently empty function included for symmetry with
        the HDMIOutFrontend class

        """
        pass

    @staticmethod
    def checkhierarchy(description):
        return "vtc_in" in description["ip"] and "axi_gpio_hdmiin" in description["ip"]

    @property
    def mode(self):
        return VideoMode(self._capture.frame_width(), self._capture.frame_height(), 24)


_outputmodes = {
    (640, 480): 0,
    (800, 600): 1,
    (1280, 720): 2,
    (1280, 1024): 3,
    (1920, 1080): 4,
}


class HDMIOutFrontend(VideoOutFrontend, DefaultHierarchy):
    """Class for interacting the HDMI output frontend

    This class is used for enabling the HDMI output and setting
    the desired mode of the video stream

    Attributes
    ----------
    mode : VideoMode
        Desired mode for the output video. Must be set prior
        to calling start

    """

    @staticmethod
    def checkhierarchy(description):
        return "vtc_out" in description["ip"] and "axi_dynclk" in description["ip"]

    def __init__(self, description):
        """Create the HDMI output front end

        Parameters
        ----------
        vtc_description : dict
            The IP dictionary entry for the video timing controller to use
        clock_description : dict
            The IP dictionary entry for the clock generator to use

        """
        import pynq.lib._video

        super().__init__(description)
        ip_dict = self.description["ip"]
        vtc_description = ip_dict["vtc_out"]
        clock_description = ip_dict["axi_dynclk"]
        vtc_capture_addr = vtc_description["phys_addr"]
        clock_addr = clock_description["phys_addr"]
        self._display = pynq.lib._video._display(vtc_capture_addr, clock_addr, 1)
        self.start = self._display.start
        """Start the HDMI output - requires the that mode is already set"""

        self.stop = self._display.stop
        """Stop the HDMI output"""

    @property
    def mode(self):
        """Get or set the video mode for the HDMI output, must be set to one
        of the following resolutions:

        640x480
        800x600
        1280x720
        1280x1024
        1920x1080

        Any other resolution  will result in a ValueError being raised.
        The bits per pixel will always be 24 when retrieved and ignored
        when set.

        """
        return VideoMode(self._display.frame_width(), self._display.frame_height(), 24)

    @mode.setter
    def mode(self, value):
        resolution = (value.width, value.height)
        if resolution in _outputmodes:
            self._display.mode(_outputmodes[resolution])
        else:
            raise ValueError(
                "Invalid Output resolution {}x{}".format(value.width, value.height)
            )


