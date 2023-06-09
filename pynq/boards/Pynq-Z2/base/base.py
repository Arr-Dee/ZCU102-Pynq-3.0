#   Copyright (c) 2017, Xilinx, Inc.
#   SPDX-License-Identifier: BSD-3-Clause


import pynq
from pynq import GPIO
import pynq.lib
import pynq.lib.video
import pynq.lib.audio
from .constants import *
from pynq.lib.logictools import TraceAnalyzer




class BaseOverlay(pynq.Overlay):
    """ The Base overlay for the Pynq-Z2

    This overlay is designed to interact with all of the on board peripherals
    and external interfaces of the Pynq-Z2 board. It exposes the following
    attributes:

    Attributes
    ----------
    iop_pmoda : IOP
         IO processor connected to the PMODA interface
    iop_pmodb : IOP
         IO processor connected to the PMODB interface
    iop_arduino : IOP
         IO processor connected to the Arduino interface
    iop_rpi : IOP
         IO processor connected to the RPi interface
    trace_rpi : pynq.logictools.TraceAnalyzer
        Trace analyzer block on RPi interface, controlled by PS.
    trace_pmoda : pynq.logictools.TraceAnalyzer
        Trace analyzer block on PMODA interface, controlled by PS.
    trace_pmodb : pynq.logictools.TraceAnalyzer
        Trace analyzer block on PMODB interface, controlled by PS.
    leds : AxiGPIO
         4-bit output GPIO for interacting with the green LEDs LD0-3
    buttons : AxiGPIO
         4-bit input GPIO for interacting with the buttons BTN0-3
    switches : AxiGPIO
         2-bit input GPIO for interacting with the switches SW0 and SW1
    rgbleds : [pynq.board.RGBLED]
         Wrapper for GPIO for LD4 and LD5 multicolour LEDs
    video : pynq.lib.video.HDMIWrapper
         HDMI input and output interfaces
    audio : pynq.lib.audio.Audio
         Headphone jack and on-board microphone
    pin_select : GPIO
        The pin selection between PMODA (0) and RPI header (1).

    """

    def __init__(self, bitfile, **kwargs):
        super().__init__(bitfile, **kwargs)
        if self.is_loaded():
            self.iop_pmoda.mbtype = "Pmod"
            self.iop_pmodb.mbtype = "Pmod"
            self.iop_arduino.mbtype = "Arduino"
            self.iop_rpi.mbtype = "Rpi"

            self.PMODA = self.iop_pmoda.mb_info
            self.PMODB = self.iop_pmodb.mb_info
            self.ARDUINO = self.iop_arduino.mb_info
            self.RPI = self.iop_rpi.mb_info

            self.pin_select = GPIO(GPIO.get_gpio_pin(
                self.gpio_dict['pmoda_rp_pin_sel']['index']), "out")
            self.audio = self.audio_codec_ctrl_0
            self.audio.configure()

            self.leds = self.leds_gpio.channel1
            self.switches = self.switches_gpio.channel1
            self.buttons = self.btns_gpio.channel1
            self.leds.setlength(4)
            self.switches.setlength(2)
            self.buttons.setlength(4)
            self.leds.setdirection("out")
            self.switches.setdirection("in")
            self.buttons.setdirection("in")
            self.rgbleds = ([None] * 4) + [pynq.lib.RGBLED(i)
                                           for i in range(4, 6)]

            self.trace_rpi = TraceAnalyzer(
                self.trace_analyzer_pi.description['ip'],
                PYNQZ2_RPI_SPECIFICATION)
            self.trace_pmoda = TraceAnalyzer(
                self.trace_analyzer_pi.description['ip'],
                PYNQZ2_PMODA_SPECIFICATION)
            self.trace_pmodb = TraceAnalyzer(
                self.trace_analyzer_pmodb.description['ip'],
                PYNQZ2_PMODB_SPECIFICATION)

    def select_pmoda(self):
        """Select PMODA in the shared pins.

        This is done by writing a `0` (default) to the `pin_select`
        GPIO instance.

        """
        self.pin_select.write(0)

    def select_rpi(self):
        """Select RASPBERRYPI in the shared pins.

        This is done by writing a `1` to the `pin_select`
        GPIO instance.

        """
        self.pin_select.write(1)


