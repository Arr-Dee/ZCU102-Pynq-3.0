#   Copyright (c) 2016, Xilinx, Inc.
#   SPDX-License-Identifier: BSD-3-Clause


from . import Arduino_DevMode
from . import ARDUINO_SWCFG_DIOALL
from . import ARDUINO_DIO_BASEADDR
from . import ARDUINO_DIO_TRI_OFFSET
from . import ARDUINO_DIO_DATA_OFFSET
from . import ARDUINO_CFG_DIO_ALLINPUT
from . import ARDUINO_CFG_DIO_ALLOUTPUT
from . import ARDUINO_NUM_ANALOG_PINS
from . import ARDUINO_NUM_DIGITAL_PINS




class Arduino_IO():
    """This class controls the Arduino IO pins as inputs or outputs.
    
    Note
    ----
    The parameter 'direction' determines whether the instance is input/output:
    'in'  : receiving input from offchip to onchip. 
    'out' : sending output from onchip to offchip.
    
    Note
    ----
    The index of the Arduino pins:
    upper row, from right to left: {0, 1, ..., 13}. (D0 - D13)
    lower row, from left to right: {14, 15,..., 19}. (A0 - A5)
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
    index : int
        The index of the Arduino pin, from 0 to 19.
    direction : str
        Input 'in' or output 'out'.
    
    """

    class __Arduino_IO(Arduino_DevMode):
        def __init__(self, mb_info):
            super().__init__(mb_info, ARDUINO_SWCFG_DIOALL)
            self.start()

    singleton_instance = None

    def __init__(self, mb_info, index, direction):
        """Return a new instance of a Arduino IO object.
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.
        index: int
            The index of the Arduino pin, starting from 0.
        direction : str
            Input 'in' or output 'out'.
            
        """
        num_pins = ARDUINO_NUM_ANALOG_PINS + ARDUINO_NUM_DIGITAL_PINS
        if index not in range(num_pins):
            raise ValueError("Valid pin indexes are 0 - {}."
                             .format(num_pins-1))
        if direction not in ['in', 'out']:
            raise ValueError("Direction can only be 'in', or 'out'.")

        if not Arduino_IO.singleton_instance:
            Arduino_IO.singleton_instance = Arduino_IO.__Arduino_IO(mb_info)

        self.microblaze = Arduino_IO.singleton_instance

        self.index = index
        self.direction = direction

        current_tri_val = self.microblaze.read_cmd(ARDUINO_DIO_BASEADDR +
                                                   ARDUINO_DIO_TRI_OFFSET)
        tri_mask = 1 << self.index
        if self.direction == 'in':
            current_tri_val |= tri_mask
            self.microblaze.write_cmd(ARDUINO_DIO_BASEADDR +
                                      ARDUINO_DIO_TRI_OFFSET,
                                      current_tri_val)
        else:
            current_tri_val &= ~tri_mask
            self.microblaze.write_cmd(ARDUINO_DIO_BASEADDR +
                                      ARDUINO_DIO_TRI_OFFSET,
                                      current_tri_val)

    def write(self, value):
        """Send the value to the offboard Arduino IO device.

        Note
        ----
        Only use this function when direction is 'out'.
        
        Parameters
        ----------
        value : int
            The value to be written to the Arduino IO device.
            
        Returns
        -------
        None
            
        """
        if value not in (0, 1):
            raise ValueError("Arduino IO can only write 0 or 1.")
        if not self.direction == 'out':
            raise ValueError('Arduino IO used as output, declared as input.')

        if self.index in range(ARDUINO_NUM_ANALOG_PINS +
                               ARDUINO_NUM_DIGITAL_PINS):
            if value:
                cur_val = self.microblaze.read_cmd(ARDUINO_DIO_BASEADDR +
                                                   ARDUINO_DIO_DATA_OFFSET)
                new_val = cur_val | (0x1 << self.index)
                self.microblaze.write_cmd(ARDUINO_DIO_BASEADDR +
                                          ARDUINO_DIO_DATA_OFFSET, new_val)
            else:
                cur_val = self.microblaze.read_cmd(ARDUINO_DIO_BASEADDR +
                                                   ARDUINO_DIO_DATA_OFFSET)
                new_val = cur_val & (0xffffffff ^ (0x1 << self.index))
                self.microblaze.write_cmd(ARDUINO_DIO_BASEADDR +
                                          ARDUINO_DIO_DATA_OFFSET, new_val)

    def read(self):
        """Receive the value from the offboard Arduino IO device.

        Note
        ----
        Only use this function when direction is 'in'.
        
        Returns
        -------
        int
            The data (0 or 1) on the specified Arduino IO pin.
        
        """  
        if not self.direction == 'in':
            raise ValueError('Arduino IO used as input, declared as output.')
        
        if self.index in range(ARDUINO_NUM_ANALOG_PINS +
                               ARDUINO_NUM_DIGITAL_PINS):
            raw_value = self.microblaze.read_cmd(ARDUINO_DIO_BASEADDR +
                                                 ARDUINO_DIO_DATA_OFFSET)
            return (raw_value >> self.index) & 0x1

    def _state(self):
        """Retrieve the current state of the Arduino IO.
        
        This function is usually used for debug purpose. Users should still
        rely on read() or write() to get/put a value.
        
        Returns
        -------
        int
            The data (0 or 1) on the specified Arduino IO pin.
        
        """
        if self.index in range(ARDUINO_NUM_ANALOG_PINS +
                               ARDUINO_NUM_DIGITAL_PINS):
            raw_value = self.microblaze.read_cmd(ARDUINO_DIO_BASEADDR +
                                                 ARDUINO_DIO_DATA_OFFSET)
            return (raw_value >> self.index) & 0x1


