#   Copyright (c) 2019, Xilinx, Inc.
#   SPDX-License-Identifier: BSD-3-Clause


import os
import warnings

import pynqutils

from .devicetree import get_dtbo_path

OVERLAYS_GROUP = "pynq.overlays"


def _resolve_bitstream(bitfile_path, device):
    if os.path.isfile(bitfile_path):
        return bitfile_path
    if os.path.isdir(bitfile_path + ".d") and hasattr(device, "name"):
        split_bitfile = os.path.split(bitfile_path)
        local_bitfile = pynqutils.setup_utils._find_local_overlay_res(
            device.name, split_bitfile[1], split_bitfile[0]
        )
        if local_bitfile is not None:
            return local_bitfile
    return None


def _find_dtbo_file(dtbo_path, bitfile_path):
    if os.path.exists(dtbo_path):
        return os.path.abspath(dtbo_path)
    relative_path = os.path.join(os.path.dirname(bitfile_path), dtbo_path)
    if os.path.exists(relative_path):
        return relative_path
    return None


class Bitstream:
    """This class instantiates the meta class for PL bitstream (full/partial).

    Attributes
    ----------
    bitfile_name : str
        The absolute path or name of the bit file as a string.
    dtbo : str
        The absolute path of the dtbo file as a string.
    partial : bool
        Flag to indicate whether or not the bitstream is partial.
    bit_data : dict
        Dictionary storing information about the bitstream.
    binfile_name : str
        The absolute path or name of the bin file as a string.
    firmware_path : str
        The absolute path of the bin file in the firmware folder.
    timestamp : str
        Timestamp when loading the bitstream. Format:
        year, month, day, hour, minute, second, microsecond

    """

    def __init__(self, bitfile_name, dtbo=None, partial=False, device=None):
        """Return a new Bitstream object.

        Users can either specify an absolute path to the bitstream file
        (e.g. '/home/xilinx/pynq/overlays/base/base.bit'),
        or a relative path within an overlay folder.
        (e.g. 'base.bit' for base/base.bit).

        Note
        ----
        `self.bitfile_name` always stores the absolute path of the bitstream.
        `self.dtbo` always stores the absolute path of the dtbo file.

        Parameters
        ----------
        bitfile_name : str
            The absolute path or name of the bit file as a string.
        dtbo : str
            The relative or absolute path to the device tree segment.
        partial : bool
            Flag to indicate whether or not the bitstream is partial.

        """
        if not isinstance(bitfile_name, str):
            raise TypeError("Bitstream name has to be a string.")
        if device is None:
            from .pl_server.device import Device

            device = Device.active_device
        self.device = device

        # self.xsa = None
        # if bitfile_name.endswith(".xsa"):
        #    self.xsa_filepath = bitfile_name
        #    self.xsa = pynqutils.build_utils.XsaParser(bitfile_name)
        #    bitfile_name = self.xsa.bitstreamPaths[0]
        #    self.xsa.load_bdc_metadata()

        bitfile_overlay_abs_lst = []
        if os.path.isabs(bitfile_name):
            bitfile_abs = _resolve_bitstream(bitfile_name, device)
        else:
            bitfile_abs = _resolve_bitstream(os.path.abspath(bitfile_name), device)
            overlays_ext_man = pynqutils.setup_utils.ExtensionsManager(OVERLAYS_GROUP)
            paths = [overlays_ext_man.extension_path(OVERLAYS_GROUP)]
            paths += overlays_ext_man.paths
            for path in paths:
                for p in [os.path.join(path, os.path.splitext(bitfile_name)[0]), path]:
                    bitfile_overlay_abs = _resolve_bitstream(
                        os.path.join(p, bitfile_name), device
                    )
                    if bitfile_overlay_abs:
                        bitfile_overlay_abs_lst.append(bitfile_overlay_abs)
        if bitfile_abs:
            self.bitfile_name = bitfile_abs
        elif bitfile_overlay_abs_lst:
            self.bitfile_name = bitfile_overlay_abs_lst[0]
        else:
            raise IOError("Bitstream file {} does not exist.".format(bitfile_name))

        if bitfile_abs and bitfile_overlay_abs_lst or len(bitfile_overlay_abs_lst) > 1:
            msg = (
                "The provided name '{}' resulted in multiple possible "
                "matches:\n - ".format(bitfile_name)
            )
            if bitfile_abs:
                msg += "{}\n - ".format(bitfile_abs)
            msg += "\n - ".join(bitfile_overlay_abs_lst)
            msg += (
                "\nThe first entry of this list, '{}', will be used, "
                "please provide the full path in case your target file "
                "was a different one in this list.".format(self.bitfile_name)
            )
            warnings.warn(msg, UserWarning)

        self.dtbo = None
        default_dtbo = get_dtbo_path(self.bitfile_name)
        if dtbo is None:
            if os.path.exists(default_dtbo):
                self.dtbo = default_dtbo
        else:
            self.dtbo = _find_dtbo_file(dtbo, self.bitfile_name)
            if self.dtbo is None:
                raise IOError("DTBO file {} does not exist.".format(dtbo))

        self.bit_data = dict()
        self.binfile_name = ""
        self.firmware_path = ""
        self.timestamp = ""
        self.partial = partial

    def download(self, parser=None):
        """Download the bitstream onto PL and update PL information.

        If device tree blob has been specified during initialization, this
        method will also insert the corresponding device tree blob into the
        system. This is same for both full bitstream and partial bitstream.

        Note
        ----
        For partial bitstream, this method does not guarantee isolation between
        static and dynamic regions.

        Returns
        -------
        None

        """
        self.device.download(self, parser)

    def gen_cache(self, parser=None):
        """ Generates the pickled metadata cache in pl_server/ even if no download has occurred """
        self.device.gen_cache(self, parser)

    def remove_dtbo(self):
        """Remove dtbo file from the system.

        A simple wrapper of the corresponding method in the PL class. This is
        very useful for partial bitstream downloading, where loading the
        new device tree blob will overwrites the existing device tree blob
        in the same partial region.

        """
        self.device.remove_device_tree(self.dtbo)

    def insert_dtbo(self, dtbo=None):
        """Insert dtbo file into the system.

        A simple wrapper of the corresponding method in the PL class. If
        `dtbo` is None, `self.dtbo` will be used to insert the dtbo
        file. In most cases, users should just ignore the parameter
        `dtbo`.

        Parameters
        ----------
        dtbo : str
            The relative or absolute path to the device tree segment.

        """
        if dtbo:
            resolved_dtbo = _find_dtbo_file(dtbo, self.bitfile_name)
            if resolved_dtbo:
                self.dtbo = resolved_dtbo
            else:
                raise IOError("DTBO file {} does not exist.".format(dtbo))
        if not self.dtbo:
            raise ValueError("DTBO path has to be specified.")
        self.device.insert_device_tree(self.dtbo)


