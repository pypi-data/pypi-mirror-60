"""
================
Cyton Bin Parser
================
"""

import numpy as np
import logging

import os
import sys
from serial.serialutil import SerialException
import time
import struct
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta

import threading
threading.stack_size(2**26)
sys.setrecursionlimit(2**20)

TIMEOUT_QUEUE = 0.1
SAMPLE_RATE_PACK = 10
# DROP_SAMPLES = 10
# DROP_PROPORTION = 1

from queue import Empty, deque, Queue
from threading import Thread


########################################################################
class CytonBinParser(metaclass=ABCMeta):
    """
    The main objective of this class (with inheritance check) create a
    background process for read and other for deserialize data and serve their
    content in queue buffers.
    """

    # Flags
    RAW = False
    READING = None
    BOARDMODE = None

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        self._data_eeg = Queue()
        # self._data_serial = Queue()
        self._data_serial = deque()
        self._data_packs = Queue()

        # self._serial_buffer = Queue(maxsize=100)
        # [self._serial_buffer.put(0) for i in range(100)]

        self._unsampled = Queue(maxsize=3)
        [self._unsampled.put([0] * 8) for i in range(3)]

        self.stop()

        self._valid = 1
        self._no_valid = 1
        self._last_marker = 0
        self._drop_proportion = 1

        self.reset_input_buffer()

    # ----------------------------------------------------------------------
    @abstractmethod
    def start(self):
        """Device handled process, start data stream."""
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def stop(self):
        """Device handled process, stop data stream."""
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def read(self):
        """Device handled process, read binary data."""
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def write(self):
        """"""
        """Device handled process, write bytes."""
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def get_board_mode(self):
        """Device handled process, board mode."""
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def scale_factor_eeg(self):
        """Device handled process, scale factor."""
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def daisy(self):
        """Device handled process, daisy board."""
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def reset_input_buffer(self):
        """Device handled process, flush input data."""
        pass

    # ----------------------------------------------------------------------
    @property
    @abstractmethod
    def bin_header(self):
        """"""
        pass

    # # ----------------------------------------------------------------------
    # @property
    # @abstractmethod
    # def sample_rate(self):
        # """"""
        # pass

    # ----------------------------------------------------------------------
    @property
    def eeg_buffer(self):
        """Return the deserialized data buffer."""

        return self._data_eeg

    # ----------------------------------------------------------------------
    @property
    def eeg_serial(self):
        """Return the binary data buffer."""

        return self._data_serial

    # ----------------------------------------------------------------------
    @property
    def eeg_pack(self):
        """Return the packed data buffer."""

        return self._data_packs

    # ----------------------------------------------------------------------
    def reset_buffers(self):
        """Discard buffers."""

        try:
            with self._data_eeg.mutex:
                self._data_eeg.queue.clear()
        except:
            while not self._data_eeg.empty():
                self._data_eeg.get()

        try:
            with self._data_serial.mutex:
                self._data_serial.queue.clear()
        except:
            self._data_serial.clear()
        else:
            while not self._data_serial.empty():
                self._data_serial.get()

        try:
            with self._data_packs.mutex:
                self._data_packs.queue.clear()
        except:
            while not self._data_packs.empty():
                self._data_packs.get()

    # ----------------------------------------------------------------------
    def start_collect(self, buffer_size=2**8, clear=True, raw=None):
        """Start a data collection asynchronously.

        Create a background process for read, deserialize and put data on a
        queue, the proces can be stoped colling `stop_collect`.

        Parameters
        ----------
        buffer_size: int, optional
            The size of characters for read from serial device.
        clear : bool, optional
            Reset buffer before start data collect.
        raw : bool, optional
            Ignore the deserialize process, all data is stored in binary format.
        """

        if clear:
            self.reset_buffers()

        if not raw is None:
            self.RAW = raw

        self.BOARDMODE = self.get_board_mode()
        self._daisy = self.daisy()
        self.READING = True
        self.start()  # start stream

        # Thread for read data
        if hasattr(self, "thread_data_collect") and self.thread_data_collect.isAlive():
            pass
        else:
            self.thread_data_collect = Thread(target=self.collect_data, args=(buffer_size, ))
            # self.thread_data_collect = Process(target=self.collect_data, args=(buffer_size, ))
            self.thread_data_collect.start()

        if not self.RAW:
            # Thread for deserialize data
            if hasattr(self, "thread_deserialize") and self.thread_deserialize.isAlive():
                pass
            else:
                self.thread_deserialize = Thread(target=self.deserialize_data)
                # self.thread_deserialize = Process(target=self.deserialize_data)
                self.thread_deserialize.start()

    # ----------------------------------------------------------------------
    def stop_collect(self):
        """Stop a data collection that run asynchronously."""

        self.READING = False
        self.stop()  # stop stream

    # ----------------------------------------------------------------------
    def collect(self, s=1, buffer_size=2**8, clear=True, raw=False):
        """Start a synchronous process for collect data.

        This call will hang until time completed.

        Parameters
        ----------
        s : int, optional
            Seconds for data collection.
        buffer_size: int, optional
            The size of characters for read from serial device.
        clear : bool, optional
            Reset buffer before start data collect.
        raw : bool, optional
            Ignore the deserialize process, all data is stored in binary format.
        """

        if clear:
            self.reset_buffers()

        self.RAW = raw

        self.start_collect(buffer_size)
        time.sleep(s)
        self.stop_collect()

    # ----------------------------------------------------------------------
    def collect_data(self, size=2**8):
        """Load binary data and put in a queue.

        For optimizations issues the data must be read in packages but write one
        to one in a queue, this method must be executed on a thread.

        Parameters
        ----------
        size : int, optional
            The buffer length for read.

        """
        # Flush input buffer, discarding all its contents.
        self.reset_input_buffer()

        # i = 0
        while self.READING:
            # i += 1
            # if i >= 100:
                # # self.all_is_right()
                # i = 0
            try:
                # [self._data_serial.append(data) for data in self.read(size)]
                self._data_serial.extend(self.read(size))
                # [self._data_serial.put(data) for data in self.read(size)]
            except SerialException as e:
                logging.error(e)

    # ----------------------------------------------------------------------
    def pack_data(self, milliseconds=100):
        """Create packages for specified time length.

        This process run in background.

        Parameters
        ----------
        milliseconds : int, optional
            The time length for packages.

        Returns
        -------
        int
            Number of samples for each package.

        """

        #samples = int(round(self.sample_rate * (milliseconds / 1000)))

        self.pack_time = milliseconds

        if hasattr(self, "thread_pack") and self.thread_pack.isAlive():
            pass
        else:
            self.thread_pack = Thread(target=self.pack_data_samples, args=(milliseconds, ))
            # self.thread_pack = Process(target=self.pack_data_samples, args=(milliseconds, ))
            self.thread_pack.start()

        # return samples

    # ----------------------------------------------------------------------
    def pack_data_samples(self, milliseconds):
        """Create packages for specified size.

        Parameters
        ----------
        samples : int, optional
            The number of samples for create packages.

        """

        while self.READING or not self._data_eeg.empty():

            pack = [self._data_eeg.get() for i in range(2)]
            while pack[-1][4] - pack[0][4] < timedelta(milliseconds=milliseconds):
                pack.extend([self._data_eeg.get() for i in range(SAMPLE_RATE_PACK)])

            pack_smp = np.array([p[0] for p in pack])
            pack_eeg = np.array([p[1] for p in pack])
            pack_aux = np.array([p[2] for p in pack])
            pack_foo = np.array([int(p[3], 16) for p in pack])
            pack_datetime = np.array([p[4].timestamp() for p in pack])
            # self._data_packs.put([pack_smp.T, pack_eeg, pack_aux.T, pack_foo.T, pack_datetime.T])
            self._data_packs.put([pack_smp, pack_eeg, pack_aux, pack_foo, pack_datetime])

        # Call again
        if self.READING:
            self.pack_data_samples(samples)

    # ----------------------------------------------------------------------
    def deserialize_data(self):
        """Extract data from binary format.

        The binary format is the more efficient way to get data, this method
        must be executed on a thread.

        """
        # # This deserialize call will end when there is no data to process or
        # # device is not in reading mode
        # # while self.READING and not self._data_serial.empty():
        # while self.READING:

            # while self._data_serial.qsize() < 100:
                # time.sleep(0.01)
                # pass

            # try:
                # # Wait for a start header
                # while self._data_serial.get(block=True, timeout=TIMEOUT_QUEUE) != self.bin_header:
                    # pass

                # while self._data_serial.qsize() < 50:
                    # time.sleep(0.01)
                    # pass

                # sample = self._data_serial.get(block=True, timeout=TIMEOUT_QUEUE)
                # eeg = [self._data_serial.get(block=True, timeout=TIMEOUT_QUEUE) for i in range(24)]
                # aux = [self._data_serial.get(block=True, timeout=TIMEOUT_QUEUE) for i in range(6)]
                # stop_byte = self._data_serial.get(block=True, timeout=TIMEOUT_QUEUE)
            # except Empty:
                # continue
            # try:
                # if hex(stop_byte)[-2].lower() != 'c':
                    # self._no_valid += 1
                    # logging.warning(f'{self}: Invalid stop byte {hex(stop_byte)} for sample {sample}, {100*(self._no_valid/self._valid):.3f}% loss')
                    # logging.warning(f'Data serial buffer: {self._data_serial.qsize()}')
                    # continue
                # else:
                    # self._valid += 1
                    # self.auto_drop()
            # except TypeError:
                # continue

        # This deserialize call will end when there is no data to process or
        # device is not in reading mode
        while self.READING:

            # # while len(self._data_serial) < 33:
                # # time.sleep(0.01)
                # # pass

            try:
                # Wait for a start header
                while self._data_serial.popleft() != self.bin_header:
                    pass

                # while len(self._data_serial) < 32:
                    # time.sleep(0.01)
                    # pass

                sample = self._data_serial.popleft()
                eeg = [self._data_serial.popleft() for i in range(24)]
                aux = [self._data_serial.popleft() for i in range(6)]
                stop_byte = self._data_serial.popleft()
            except:
                continue
            try:
                if hex(stop_byte)[-2].lower() != 'c':
                    self._no_valid += 1
                    # logging.warning(f'{self}: Invalid stop byte {hex(stop_byte)} for sample {sample}?, {100*(self._no_valid/self._valid):.3f}% loss')
                    # logging.warning(f'Data serial buffer: {len(self._data_serial)}')
                    continue
                else:
                    self._valid += 1
                    self.auto_drop(self._valid)
            except TypeError:
                continue

            # Scale factor to volts
            # first complete to 32-bit, Python not support 24-bit natively
            # finally scale with the correct gain for each channel
            eeg = sum([eeg[i:i + 3] + [0] for i in range(0, len(eeg), 3)], [])
            eeg = list(memoryview(bytearray(eeg)).cast('I'))  # I for 32-bit
            eeg = list(map(lambda _: _[0] * _[1],
                           zip(eeg, self.scale_factor_eeg)))  # scale

            # Update unsampled queue
            self._unsampled.get()
            self._unsampled.put(eeg)

            if self._daisy:
                m, n, o = list(self._unsampled.queue)
                # self._unsampled.get()

                if sample % 2:  # odd
                    eeg = np.average([m, o], axis=0).tolist() + n
                else:  # pair
                    eeg = n + np.average([m, o], axis=0).tolist()

            # Deserialize Aux Data
            aux = self.deserialize_aux(stop_byte, aux)

            # Return only channels selected
            eeg = [eeg[key] for key in self.montage.keys()]

            # The eeg buffer contain lists with data deserialized
            self._data_eeg.put([sample, eeg, aux, hex(stop_byte), datetime.now()])

            logging.debug(f'Sample {sample} ok')

        # Call again
        if self.READING:
            self.deserialize_data()

    # ---------------------------------------------------------------------
    def auto_drop(self, counter, samples=20):
        """Drop data automatically when they accumulate a lot."""

        if not (counter % samples):

            std = len(self._data_serial)

            if std > (33 * 90) * 5:
                self._drop_proportion += 0.1
            elif std < (33 * 90) * 2:
                self._drop_proportion -= 0.5

            for _ in range(33 * int(samples * self._drop_proportion)):
                try:
                    self._data_serial.popleft()
                except:
                    return

    # ----------------------------------------------------------------------
    def deserialize_aux(self, stop_byte, aux):
        """Determine the content of `AUX` bytes and format it.

        Auxialiar data could contain different kind of information: accelometer,
        user defined, time stamped and digital or analog inputs.
        The context of `AUX` bytes are determined by the stop byte.

        If `stop_byte` is `0xc0` the `AUX` bytes contain `Standard with accel`,
        this data are packaged at different frequency, they will be show up each
        10 or 11 packages, the final list will contain accelometer value in `G`
        units for axis `X`, `Y` and `Z` respectively and `None` when are not
        availables.

        If `stop_byte` is `0xc1` the `AUX` bytes contain `Standard with raw aux`,
        there are 3 types of raw data: `digital` in wich case the final list
        will contain the values for `D11`, `D12`, `D13`, `D17`, `D18`; `analog`
        with the values for `A7` (`D13`), `A6` (`D12`), `A5` (`D11`); `markers`
        data contain the the marker sended with `send_marker()` method.

        Parameters
        ----------
        stop_byte : int
             0xCX where X is 0-F in hex.

        aux : int
            6 bytes of data defined and parsed based on the `Footer` bytes.


        Returns
        -------
        list
            Correct data formated.

        """

        # Standard with accel
        if stop_byte == 0xc0:
            if aux.count(0) >= 3:
                return None
            else:
                return [0.002 * d / 16
                        for d in struct.unpack('>hhh', bytearray(aux))]

        # Standard with raw aux
        elif stop_byte == 0xc1:

            if self.BOARDMODE == b'analog':
                # A7, A6, A5
                # D13, D12, D11
                return aux[1::2]

            elif self.BOARDMODE == b'digital':
                # D11, D12, D13, D17, D18
                aux.pop(4)
                return aux

            elif self.BOARDMODE == b'marker':
                # Some time for some reason, marker not always send back from
                # OpenBCI, so this module implement a strategy to send a burst of
                # markers but read back only one.
                marker = aux.pop(1)
                if marker:
                    if (time.time() - self._last_marker) > 0.3:
                        self._last_marker = time.time()
                        return marker

                return 0

        # User defined
        elif stop_byte == 0xc2:
            pass

        # Time stamped set with accel
        elif stop_byte == 0xc3:
            pass

        # Time stamped with accel
        elif stop_byte == 0xc4:
            pass

        # Time stamped set with raw auxcalculate_sample_rate
        elif stop_byte == 0xc5:
            pass

        # Time stamped with raw aux
        elif stop_byte == 0xc6:
            pass

        return aux

    # ----------------------------------------------------------------------
    def calculate_sample_rate(self, seconds=5, buffer_size=2**8):
        """Calculate the sample rate with real data transmission.

        Parameters
        ----------
        seconds : int, optional
             Seconds for transmission.

        buffer_size : int, optional
            The size of characters for read from serial device.

        """

        # TODO: Calculate with timestamp

        # self.collect(seconds, buffer_size)
        # time.sleep(0.2)
        # sample_rate = self.eeg_buffer.qsize() / seconds
        # self.sample_rate_ = sample_rate
