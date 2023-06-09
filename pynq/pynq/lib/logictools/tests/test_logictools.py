#   Copyright (c) 2016, Xilinx, Inc.
#   SPDX-License-Identifier: BSD-3-Clause


from random import randint
import numpy as np
import pytest
from pynq import Overlay
from pynq.lib.logictools import LogicToolsController
from pynq.lib.logictools import ARDUINO
from pynq.lib.logictools import MAILBOX_OFFSET
from pynq.lib.logictools import MAX_NUM_TRACE_SAMPLES




try:
    ol = Overlay('logictools.bit', download=False)
    flag = True
except IOError:
    flag = False


@pytest.mark.skipif(not flag, reason="need correct overlay to run")
def test_controller_init():
    """Test for logic tools controller.

    First test whether LogicToolsController can return an object without 
    exceptions.

    """
    ol.download()
    exception_raised = False
    controller1 = controller2 = None
    try:
        controller1 = LogicToolsController(ARDUINO,
                                           'PYNQZ1_LOGICTOOLS_SPECIFICATION')
        controller2 = LogicToolsController(ARDUINO,
                                           'PYNQZ1_LOGICTOOLS_SPECIFICATION')
    except RuntimeError:
        exception_raised = True
    assert not exception_raised, \
        'LogicToolsController() initialization failed.'
    del controller1, controller2


@pytest.mark.skipif(not flag, reason="need correct overlay to run")
def test_controller_mailbox():
    """Test for logic tools controller.

    Test whether control parameters can be written into/read from the mailbox.

    """
    ol.download()
    controller = LogicToolsController(ARDUINO,
                                      'PYNQZ1_LOGICTOOLS_SPECIFICATION')
    data_write = list()
    for i in range(10):
        data_write.append(randint(0, pow(2, 32) - 1))

    controller.write_control(data_write)
    for index in range(10):
        data_read = controller.read(MAILBOX_OFFSET + 4 * index)
        assert data_write[index] == data_read, \
            'Mailbox location {} read {} != write {}.'.format(
                index, data_read, data_write)
    del controller


@pytest.mark.skipif(not flag, reason="need correct overlay to run")
def test_controller_buffer():
    """Test for logic tools controller.

    Test the capability to allocate buffers.

    """
    ol.download()
    controller = LogicToolsController(ARDUINO,
                                      'PYNQZ1_LOGICTOOLS_SPECIFICATION')
    num_samples = MAX_NUM_TRACE_SAMPLES + 1
    test_data_32_addr = controller.allocate_buffer(
        'test_data_32_buf', num_samples, data_type='unsigned int')
    test_data_64_addr = controller.allocate_buffer(
        'test_data_64_buf', num_samples, data_type='unsigned long long')
    assert test_data_32_addr is not None, 'Failed to allocate memory.'
    assert test_data_64_addr is not None, 'Failed to allocate memory.'
    del controller


@pytest.mark.skipif(not flag, reason="need correct overlay to run")
def test_controller_data():
    """Test for logic tools controller.

    Test writing and reading the data from the allocated buffers.

    """
    ol.download()
    controller = LogicToolsController(ARDUINO,
                                      'PYNQZ1_LOGICTOOLS_SPECIFICATION')
    num_samples = MAX_NUM_TRACE_SAMPLES + 1
    data_32_write = np.random.randint(0, 2**32, num_samples, dtype=np.uint32)
    data_64_write = np.random.randint(0, 2**64, num_samples, dtype=np.uint64)
    _ = controller.allocate_buffer('test_data_32_buf',
                                   num_samples, data_type='unsigned int')
    _ = controller.allocate_buffer('test_data_64_buf',
                                   num_samples, data_type='unsigned long long')
    for index in range(num_samples):
        controller.buffers['test_data_32_buf'][index] = data_32_write[index]
        controller.buffers['test_data_64_buf'][index] = data_64_write[index]

    data_32_read = controller.ndarray_from_buffer(
        'test_data_32_buf', num_samples * 4, dtype=np.uint32)
    data_64_read = controller.ndarray_from_buffer(
        'test_data_64_buf', num_samples * 8, dtype=np.uint64)

    assert np.array_equal(data_32_read, data_32_write), \
        'Reading wrong numpy uint32 data.'
    assert np.array_equal(data_64_read, data_64_write), \
        'Reading wrong numpy uint64 data.'

    del data_32_read, data_32_write, data_64_read, data_64_write

    controller.reset_buffers()
    assert len(controller.buffers) == 0, \
        'Buffers are not empty after resetting.'

    del controller


