#   Copyright (c) 2018, Xilinx, Inc.
#   SPDX-License-Identifier: BSD-3-Clause


import os

LIB_SEARCH_PATH = os.path.dirname(os.path.realpath(__file__))

# Transcribed from the ZCU104 HDMI reference design
IDT_8T49N24X_XTAL_FREQ = 40000000  # The freq of the crystal in Hz
IDT_8T49N24X_FVCO_MAX = 4000000000  # Max VCO Operating Freq in Hz
IDT_8T49N24X_FVCO_MIN = 3000000000  # Min VCO Operating Freq in Hz

IDT_8T49N24X_FOUT_MAX = 400000000  # Max Output Freq in Hz
IDT_8T49N24X_FOUT_MIN = 8000       # Min Output Freq in Hz

IDT_8T49N24X_FIN_MAX = 875000000   # Max Input Freq in Hz
IDT_8T49N24X_FIN_MIN = 8000        # Min Input Freq in Hz

IDT_8T49N24X_FPD_MAX = 128000      # Max Phase Detector Freq in Hz
IDT_8T49N24X_FPD_MIN = 8000        # Min Phase Detector Freq in Hz

IDT_8T49N24X_P_MAX = 4194304       # pow(2,22) - Max P div value
IDT_8T49N24X_M_MAX = 16777216      # pow(2,24) - Max M mult value

# Initial configuration that sets up a free-running clock
IDT_Synth = [
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE, 0xEF, 0x00, 0x03, 0x00, 0x31, 0x00,
    0x04, 0x89, 0x00, 0x00, 0x01, 0x00, 0x63, 0xC6, 0x07, 0x00, 0x00, 0x77,
    0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x01,
    0x3F, 0x00, 0x28, 0x00, 0x1A, 0xCC, 0xCD, 0x00, 0x01, 0x00, 0x00, 0xD0,
    0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x0C, 0x00, 0x00,
    0x00, 0x44, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0B,
    0x00, 0x00, 0x0B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x89, 0x0A, 0x2B, 0x20,
    0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x27, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00

]

# The frequency of the crystal connected to the XA/XB pins of the Si5324 in Hz.
SI5324_XTAL_FREQ = 114285000

# Error codes generated by the functions in this driver.
SI5324_SUCCESS = 0  # Operation was successful
SI5324_ERR_IIC = -1  # IIC error occurred
SI5324_ERR_FREQ = -2  # Could not calculate frequency setting
SI5324_ERR_PARM = -3  # Invalid parameter

# The following constants define the clock input select values.
SI5324_CLKSRC_CLK1 = 1  # Use clock input 1
SI5324_CLKSRC_CLK2 = 2  # Use clock input 2
SI5324_CLKSRC_XTAL = 3  # Use crystal (free running mode)

# The following constants define the limits of the Si5324 frequencies.
SI5324_FOSC_MIN = 4850000000  # Minimum oscillator frequency
SI5324_FOSC_MAX = 5670000000  # Maximum oscillator frequency
SI5324_F3_MIN = 10000  # 2000 /**< Minimum phase detector frequency
SI5324_F3_MAX = 2000000  # Maximum phase detector frequency
SI5324_FIN_MIN = 2000  # Minimum input frequency
SI5324_FIN_MAX = 710000000  # Maximum input frequency
SI5324_FOUT_MIN = 2000  # Minimum output frequency
SI5324_FOUT_MAX = 945000000  # Maximum output frequency

# Minimum N1_HS setting (4 and 5 are for higher output frequencies*/
SI5324_N1_HS_MIN = 6
SI5324_N1_HS_MAX = 11  # Maximum N1_HS setting
SI5324_NC_LS_MIN = 1  # Minimum NCn_LS setting (1 and even values)

# Maximum NCn_LS setting (1 and even values)
SI5324_NC_LS_MAX = 0x100000
SI5324_N2_HS_MIN = 4  # Minimum NC2_HS setting
SI5324_N2_HS_MAX = 11  # Maximum NC2_HS setting
SI5324_N2_LS_MIN = 2  # Minimum NC2_LS setting (even values only)

# Maximum NC2_LS setting (even values only)
SI5324_N2_LS_MAX = 0x100000
SI5324_N3_MIN = 1  # Minimum N3n setting
SI5324_N3_MAX = 0x080000  # Maximum N3n setting


