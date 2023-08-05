"""
=====
Cyton
=====

The OpenBCI Cyton PCBs were designed with Design Spark, a free PCB capture
program.


Cyton Board Specs:

* Power with 3-6V DC Battery ONLY
* PIC32MX250F128B Micrcontroller with chipKIT UDB32-MX2-DIP bootloader
* ADS1299 Analog Front End
* LIS3DH 3 axis Accelerometer
* RFduino BLE radio
* Micro SD card slot
* Voltage Regulation (3V3, +2.5V, -2.5V)
* Board Dimensions 2.41 x 2.41 (octogon has 1 edges) [inches]
* Mount holes are 1/16 ID, 0.8 x 2.166 on center [inches]


Data Format
===========

Binary Format
-------------

+-------------+----------------------------------------------------------------+
| **Byte No** | **Description**                                                |
+-------------+----------------------------------------------------------------+
| 1           | Start byte, always `0xA0`                                      |
+-------------+----------------------------------------------------------------+
| 2           | Sample Number                                                  |
+-------------+----------------------------------------------------------------+
| 3-26        | EEG Data, values are 24-bit signed, MSB first                  |
+-------------+----------------------------------------------------------------+
| 27-32       | Aux Data                                                       |
+-------------+----------------------------------------------------------------+
| 33          | Footer, `0xCX` where `X` is 0-F in hex                         |
+-------------+----------------------------------------------------------------+



EEG Data for 8 channels
-----------------------

24-Bit Signed.

+-------------+----------------------------------------------------------------+
| **Byte No** | **Description**                                                |
+-------------+----------------------------------------------------------------+
| 3-5         | Data value for EEG channel 1                                   |
+-------------+----------------------------------------------------------------+
| 6-8         | Data value for EEG channel 2                                   |
+-------------+----------------------------------------------------------------+
| 9-11        | Data value for EEG channel 3                                   |
+-------------+----------------------------------------------------------------+
| 12-14       | Data value for EEG channel 4                                   |
+-------------+----------------------------------------------------------------+
| 15-17       | Data value for EEG channel 5                                   |
+-------------+----------------------------------------------------------------+
| 18-20       | Data value for EEG channel 6                                   |
+-------------+----------------------------------------------------------------+
| 21-23       | Data value for EEG channel 7                                   |
+-------------+----------------------------------------------------------------+
| 24-26       | Data value for EEG channel 8                                   |
+-------------+----------------------------------------------------------------+


EEG Data for 16 channels
------------------------

24-Bit Signed.

+----------------------------+--------------------------+--------------------------+
| **Received**               | **Upsampled board data** | **Upsampled daisy data** |
+--------------+-------------+--------------------------+--------------------------+
| sample(3)    |             | avg(sample(1),sample(3)) | sample(2)                |
+--------------+-------------+--------------------------+--------------------------+
|              | sample(4)   | sample(3)                | avg(sample(2),sample(4)) |
+--------------+-------------+--------------------------+--------------------------+
| sample(5)    |             | avg(sample(3),sample(5)) | sample(4)                |
+--------------+-------------+--------------------------+--------------------------+
|              | sample(6)   | sample(5)                | avg(sample(4),sample(6)) |
+--------------+-------------+--------------------------+--------------------------+
| sample(7)    |             | avg(sample(5),sample(7)) | sample(7)                |
+--------------+-------------+--------------------------+--------------------------+
|              | sample(8)   | sample(7)                | avg(sample(6),sample(8)) |
+--------------+-------------+--------------------------+--------------------------+


Aux Data
--------

16-Bit Signed.

+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+
| **Stop Byte (33)** | **Byte 27** | **Byte 28** | **Byte 29** | **Byte 30** | **Byte 31** | **Byte 32** |          **Name**             |
+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+
| 0xc0               | AX1         | AX2         | AY1         | AY2         | AZ1         | AZ2         | Standard with accel           |
+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+
| 0xC1               | UDF         | UDF         | UDF         | UDF         | UDF         | UDF         | Standard with raw aux         |
+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+
| 0xC2               | UDF         | UDF         | UDF         | UDF         | UDF         | UDF         | User defined                  |
+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+
| 0xC3               | *AC*        | *AV*        | T3          | T2          | T1          | T0          | Time stamped set with accel   |
+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+
| 0xC4               | *AC*        | *AV*        | T3          | T2          | T1          | T0          | Time stamped with accel       |
+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+
| 0xC5               | UDF         | UDF         | T3          | T2          | T1          | T0          | Time stamped set with raw aux |
+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+
| 0xC6               | UDF         | UDF         | T3          | T2          | T1          | T0          | Time stamped with raw aux     |
+--------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------------------------+


Aux Data
--------

16-Bit Signed.

+-------------+-------------+
| **Byte 27** | **Byte 28** |
+-------------+-------------+
|  X          | AX1         |
+-------------+-------------+
|  x          | AX0         |
+-------------+-------------+
|  Y          | AY1         |
+-------------+-------------+
|  y          | AY0         |
+-------------+-------------+
|  Z          | AZ1         |
+-------------+-------------+
|  z          | AZ0         |
+-------------+-------------+
"""
import logging
import sys
import serial
import os
import time

import asyncore
import atexit
import socket
import requests

from threading import Thread
from openbci.acquisition.cyton_bin_parser import CytonBinParser

DEFAULT_LOCAL_IP = "192.168.1.1"


########################################################################
class Cyton(CytonBinParser):
    """
    The Cyton data format and SDK define all interactions and capabilities of
    the board, the full instructions can be found in the official package.

      * https://docs.openbci.com/Hardware/03-Cyton_Data_Format
      * https://docs.openbci.com/OpenBCI%20Software/04-OpenBCI_Cyton_SDK

    """

    VREF = 4.5

    BIN_HEADER = 0xa0

    START_STREAM = b'b'
    STOP_STREAM = b's'

    DEACTIVATE_CHANEL = b'12345678qwertyui'
    ACTIVATE_CHANEL = b'!@#$%^&*QWERTYUI'
    CHANNEL_SETTING = b'12345678QWERTYUI'

    TEST_GND = b'0'      # Connect to internal GND (VDD - VSS)
    TEST_1X_SLOW = b'-'  # Connect to test signal 1xAmplitude, slow pulse
    TEST_1X_FAST = b'='  # Connect to test signal 1xAmplitude, fast pulse
    TEST_DC = b'p'       # Connect to DC signal
    TEST_2X_SLOW = b'['  # Connect to test signal 2xAmplitude, slow pulse
    TEST_2X_FAST = b']'  # Connect to test signal 2xAmplitude, fast pulse

    POWER_DOWN_ON = b'0'
    POWER_DOWN_OFF = b'1'

    GAIN_1 = b'0'
    GAIN_2 = b'1'
    GAIN_4 = b'2'
    GAIN_6 = b'3'
    GAIN_8 = b'4'
    GAIN_12 = b'5'
    GAIN_24 = b'6'

    ADSINPUT_NORMAL = b'0'
    ADSINPUT_SHORTED = b'1'
    ADSINPUT_BIAS_MEAS = b'2'
    ADSINPUT_MVDD = b'3'
    ADSINPUT_TEMP = b'4'
    ADSINPUT_TESTSIG = b'5'
    ADSINPUT_BIAS_DRP = b'6'
    ADSINPUT_BIAS_DRN = b'7'

    BIAS_REMOVE = b'0'
    BIAS_INCLUDE = b'1'

    SRB2_DISCONNECT = b'0'
    SRB2_CONNECT = b'1'

    SRB1_DISCONNECT = b'0'
    SRB1_CONNECT = b'1'

    DEFAULT_CHANNELS_SETTINGS = b'd'
    DEFAULT_CHANNELS_SETTINGS_REPORT = b'D'

    TEST_SIGNAL_NOT_APPLIED = b'0'
    TEST_SIGNAL_APPLIED = b'1'

    SD_DATA_LOGGING_5MIN = b'A'
    SD_DATA_LOGGING_15MIN = b'S'
    SD_DATA_LOGGING_30MIN = b'F'
    SD_DATA_LOGGING_1HR = b'G'
    SD_DATA_LOGGING_2HR = b'H'
    SD_DATA_LOGGING_4HR = b'J'
    SD_DATA_LOGGING_12HR = b'K'
    SD_DATA_LOGGING_24HR = b'L'
    SD_DATA_LOGGING_14S = b'a'
    SD_DATA_LOGGING_STOP = b'j'

    QUERY_REGISTER = b'?'
    SOFT_RESET = b'v'

    USE_8CH_ONLY = b'c'
    USE_16CH_ONLY = b'C'

    TIME_STAMP_ON = b'<'
    TIME_STAMP_OFF = b'>'

    SAMPLE_RATE_16KHZ = b'~0'
    SAMPLE_RATE_8KHZ = b'~1'
    SAMPLE_RATE_4KHZ = b'~2'
    SAMPLE_RATE_2KHZ = b'~3'
    SAMPLE_RATE_1KHZ = b'~4'
    SAMPLE_RATE_500HZ = b'~5'
    SAMPLE_RATE_250HZ = b'~6'
    SAMPLE_RATE_GET = b'~~'

    SAMPLE_RATE_VALUE = {
        b'~0': 16e3,
        b'~1': 8e3,
        b'~2': 4e3,
        b'~3': 2e3,
        b'~4': 1e3,
        b'~5': 500,
        b'~6': 250,
    }

    BOARD_MODE_DEFAULT = b'/0'  # Sends accelerometer data in aux bytes
    BOARD_MODE_DEBUG = b'/1'    # Sends serial output over the external serial
                                # port which is helpful for debugging.
    BOARD_MODE_ANALOG = b'/2'   # Reads from analog pins A5(D11), A6(D12) and
                                # if no wifi shield is present, then A7(D13)
                                # as well.
    BOARD_MODE_DIGITAL = b'/3'  # Reads from analog pins D11, D12 and D17.
                                # If no wifi present then also D13 and D18.
    BOARD_MODE_MARKER = b'/4'   # Turns accel off and injects markers
                                # into the stream by sending `X where X is any
                                # char to add to the first AUX byte.
    BOARD_MODE_GET = b'//'      # Get current board mode

    WIFI_SHIELD_ATTACH = b'{'
    WIFI_SHIELD_DEATTACH = b'}'
    WIFI_SHIELD_STATUS = b':'
    WIFI_SHIELD_RESET = b';'

    VERSION = b'V'

    # ----------------------------------------------------------------------
    @property
    def gain(self):
        """Vector with the gains for each channel."""

        # TODO
        # A method for change the ganancy of each channel must be writed here
        return [24, 24, 24, 24, 24, 24, 24, 24]

    # ----------------------------------------------------------------------
    @property
    def scale_factor_eeg(self):
        """Vector with the correct factors for scale eeg data samples."""

        return [self.VREF / (gain * ((2 ** 23) - 1)) for gain in self.gain]

    # ----------------------------------------------------------------------
    @property
    def bin_header(self):
        """Byte with start header."""

        return self.BIN_HEADER

    # # ----------------------------------------------------------------------
    # @property
    # def sample_rate(self):
        # """Byte with start header."""

        # return self.sample_rate_

    # ----------------------------------------------------------------------
    def start(self):
        """Start stream."""

        return self.command(self.START_STREAM)

    # ----------------------------------------------------------------------
    def stop(self):
        """Stop stream."""

        return self.command(self.STOP_STREAM)

    # ----------------------------------------------------------------------
    def deactivate_channel(self, channels):
        """Deactivate the channels specified."""

        [self.command(self.DEACTIVATE_CHANEL[ch]) for ch in channels]

    # ----------------------------------------------------------------------
    def activate_channel(self, channels):
        """Activate the channels specified."""

        chain = ''.join([chr(self.ACTIVATE_CHANEL[ch]) for ch in channels]).encode()
        self.command(chain)
        # [self.command(self.ACTIVATE_CHANEL[ch]) for ch in channels]

    # ----------------------------------------------------------------------
    def command(self, c):
        """Send a command to device.

        Before send the commmand the input buffer is cleared, and after that
        waits 300 ms for a response.

        Parameters
        ----------
        c : bytes
            Command to send.

        Returns
        -------
        str
            If the command generate a response this will be sended back.
        """

        self.reset_input_buffer()
        self.write(c)
        time.sleep(0.3)
        response = self.read(2**11)
        logging.info(f'From device {response}')

        if hasattr(response, 'encode'):
            response = response.encode()
        elif isinstance(response, (list)):
            response = ''.join([chr(r) for r in response]).encode()

        return response

    # ----------------------------------------------------------------------
    def channel_setting(self, channels,
                        power_down=POWER_DOWN_ON,
                        gain=GAIN_24,
                        input_type=ADSINPUT_NORMAL,
                        bias=BIAS_INCLUDE,
                        srb2=SRB2_CONNECT,
                        srb1=SRB1_DISCONNECT):
        """Channel Settings commands.

        Parameters
        ----------
        channels : list
            List of channels that will share the configuration specified.
        power_down : bytes, optional
            POWER_DOWN_ON (default), POWER_DOWN_OFF.
        gain: bytes, optional
            GAIN_24 (default), GAIN_12, GAIN_8, GAIN_6, GAIN_4, GAIN_2, GAIN_1.
        input_type : bytes, optional
            Select the ADC channel input source: ADSINPUT_NORMAL (default),
            ADSINPUT_SHORTED, ADSINPUT_BIAS_MEAS, ADSINPUT_MVDD, ADSINPUT_TEMP,
            ADSINPUT_TESTSIG, ADSINPUT_BIAS_DRP, ADSINPUT_BIAS_DRN,
        bias : bytes, optional
            Select to include the channel input in BIAS generation:
            BIAS_INCLUDE (default), BIAS_REMOVE.
        srb2 : bytes, optional
            Select to connect this channel’s P input to the SRB2 pin. This
            closes a switch between P input and SRB2 for the given channel,
            and allows the P input also remain connected to the ADC:
            SRB2_CONNECT (default), SRB2_DISCONNECT.
        srb1 : bytes, optional
            Select to connect all channels’ N inputs to SRB1. This effects all
            pins, and disconnects all N inputs from the ADC:
            SRB1_DISCONNECT (default), SRB1_CONNECT.

        Returns
        -------

        On success:

          * If streaming, no confirmation of success. Note: WiFi Shields will always get a response, even if streaming.
          * If not streaming, returns Success: Channel set for 3$$$, where 3 is the channel that was requested to be set.

        On failure:

          * If not streaming, NOTE: WiFi shield always sends the following responses without $$$
              * Not enough characters received, Failure: too few chars$$$ (example user sends x102000X)
              * 9th character is not the upper case `X`, Failure: 9th char not X$$$ (example user sends x1020000V)
              * Too many characters or some other issue, Failure: Err: too many chars$$$
          * If not all commands are not received within 1 second, Timeout processing multi byte message - please send all commands at once as of v2$$$

        """

        start = b'x'
        end = b'X'

        self.reset_input_buffer()

        for channel in channels:
            ch = self.CHANNEL_SETTING[channel]
            chain = b''.join([start, ch, power_down, gain, input_type, bias,
                              srb2, srb1, end])
            self.write(chain)

        time.sleep(0.3)
        return self.read(2**11)

    # ----------------------------------------------------------------------
    def leadoff_impedance(self, channels, pchan=TEST_SIGNAL_NOT_APPLIED,
                          nchan=TEST_SIGNAL_NOT_APPLIED):
        """LeadOff Impedance Commands

        Parameters
        ----------
        channels : list
            List of channels that will share the configuration specified.
        pchan : bytes, optional
            TEST_SIGNAL_NOT_APPLIED (default), TEST_SIGNAL_NOT_APPLIED.
        nchan : bytes, optional
            TEST_SIGNAL_NOT_APPLIED (default), TEST_SIGNAL_NOT_APPLIED.

        Returns
        -------

        On success:

          * If streaming, no confirmation of success. Note: WiFi Shields will always get a response, even if streaming.
          * If not streaming, returns Success: Lead off set for 4$$$, where 4 is the channel that was requested to be set.

        On failure:

          * If not streaming, NOTE: WiFi shield always sends the following responses without $$$
              * Not enough characters received, Failure: too few chars$$$ (example user sends z102000Z)
              * 5th character is not the upper case ‘Z’, Failure: 5th char not Z$$$ (example user sends z1020000X)
              * Too many characters or some other issue, Failure: Err: too many chars$$$
          * If not all commands are not received within 1 second, Timeout processing multi byte message - please send all commands at once as of v2$$$

        """

        start = b'z'
        end = b'Z'

        self.reset_input_buffer()

        for channel in channels:
            ch = chr(self.CHANNEL_SETTING[channel]).encode()
            chain = b''.join([start, ch, pchan, nchan, end])
            self.write(chain)

        time.sleep(0.3)
        return self.read(2**11)

    # ----------------------------------------------------------------------
    def get_board_mode(self):
        """The board mode determine how to deserialize the `AUX` bytes.

        Returns
        -------
        str, None
            The board mode as string or None if no response.

        """
        current_mode = self.command(self.BOARD_MODE_GET)
        if not current_mode:
            return None
        for mode in [b'analog', b'digital', b'debug', b'default', b'marker']:
            if mode in current_mode:
                return mode

    # ----------------------------------------------------------------------
    def send_marker(self, marker, burst=20):
        """Send marker to device.

        The marker sended will be added to the `AUX` bytes in the next data
        input.

        The OpenBCI markers does not work as well as expected, so this module
        implement an strategy for make it works. A burst markers are sended but
        just one are readed, this add a limitation: No more that one marker each
        300 ms are permitted.

        Parameters
        ----------
        marker : str, bytes, int
            A single value required.
        burst : int, optional
            How many times the marker will be send.

        """

        def thread_marker(marker):
            if isinstance(marker, int):
                marker = chr(marker)
            elif isinstance(marker, bytes):
                marker = marker.decode()

            for i in range(burst):
                self.write(f'`{marker}'.encode())
                time.sleep(0.007)

        self.thread_marker = Thread(target=thread_marker, args=(marker, ))
        # self.thread_marker = Process(target=thread_marker, args=(marker, ))
        self.thread_marker.start()

    # ----------------------------------------------------------------------
    def daisy(self):
        """Check if a Daisy module is attached.

        This command will activate the Daisy module is this is available.

        Returns
        -------
        bool
            Daisy module activated.

        """
        # self.command(self.SOFT_RESET)  # to update the status information
        response = self.command(self.USE_16CH_ONLY)
        # self.activate_channel(range(16))

        if not response:
            logging.warning(f"Channels no setted correctly")
            return None

        daisy = not (('no daisy to attach' in response.decode()) or ('8' in response.decode()))

        # if self.montage:
            # channels = self.montage.keys()
        if not self.montage and daisy:
            # channels = range(16)
            self.set_montage(range(16))
        elif not self.montage and not daisy:
            # channels = range(8)
            self.set_montage(range(8))

        channels = self.montage.keys()
        self.leadoff_impedance(channels, self.TEST_SIGNAL_NOT_APPLIED, self.TEST_SIGNAL_APPLIED)
        self.activate_channel(channels)

        logging.info(f"Ussing channels: {channels}")

        return daisy

    # ----------------------------------------------------------------------
    def set_montage(self, montage=None):
        """Define the information with que electrodes names.

        If a list is passed the format will be supposed with index as channels,
        the index can be set explicitly with a dictionary instead of a list.

        Parameters
        ----------
        montage : list, dict, None, optional
            Decription of channels used.
        """

        if isinstance(montage, (list, tuple, range)):
            self.montage = {i: ch for i, ch in enumerate(montage)}
        else:
            self.montage = montage


########################################################################
class FakeDevice:
    """For use without a real device connected."""

    # ----------------------------------------------------------------------
    def __init__(self, file):
        """Load a file or open one from path.

        Parameters
        ----------
        file : file object, str
            The file or file path that contain binary data for debug.
        """

        if isinstance(file, str):
            self.file = open(file, 'rb')
        else:
            self.file = file

    # ----------------------------------------------------------------------
    def read(self, size):
        """Fake read function.

        Parameters
        ----------
        size : int
            Size of input buffer.

        Returns
        -------
        bytes
            Data readed.
        """

        time.sleep(0.01)
        return [int.from_bytes(self.file.read(1), "little") for _ in range(size)]

    # ----------------------------------------------------------------------
    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""
        pass

    # ----------------------------------------------------------------------
    def write(self, data):
        """Output the given data over the serial port."""
        logging.info(f'Serial write: {data.decode()}')

    # ----------------------------------------------------------------------
    def close(self):
        """Close the serial communication."""
        pass


########################################################################
class CytonRFDuino(Cyton):
    """
    RFduino is the default communication mode for Cyton 32 bit, this set a
    serial comunication through a USB dongle with a sample frequency of `250`
    Hz, for 8 or 16 channels.
    """

    # ----------------------------------------------------------------------
    def __init__(self, port=None, montage=None, file=None, timeout=0.5, write_timeout=0.1, sample_rate='SAMPLE_RATE_250HZ'):
        """RFduino mode connection.

        Parameters
        ----------
        port : str, optional
            Specific serial port for connection.
        montage: dictl, list, optional
            Decription of channels used.
        file : str, file object, optional
            File for use in debugging mode.
        timeout: float, optional.
            Read timeout for serial connection.
        write_timeout: float, optional.
            Write timeout for serial connection.
        sample_rate: bytes, optional.
            The command for set the sample rate.

        """

        # self.sample_rate_ = self.SAMPLE_RATE_VALUE[sample_rate]
        if not sample_rate in self.SAMPLE_RATE_VALUE.keys():
            sample_rate = getattr(self, sample_rate)

        self.set_montage(montage)

        if file:
            logging.info('Running in debug mode')
            self.device_ = FakeDevice(file)
            super().__init__()

        else:
            if port is None:
                port = self._get_free_port()

            if port is None:
                logging.error("No device was auto detected.")
                sys.exit()

            try:
                self.device_ = serial.Serial(port, 115200, timeout=timeout,
                                             write_timeout=write_timeout,
                                             parity=serial.PARITY_NONE,
                                             stopbits=serial.STOPBITS_ONE)
                self.command(sample_rate)
                super().__init__()
            except Exception as e:
                logging.error(f"Impossible to connect with {port}")
                logging.error(e)
                sys.exit()

    # ----------------------------------------------------------------------
    @property
    def device(self):
        """Device manager."""

        return self.device_

    # ----------------------------------------------------------------------
    def _get_free_port(self):
        """Look for first available port with OpenBCI device.

        Returns
        -------
        str
            String with the port name or None if no ports were founded.
        """

        if os.name == 'nt':
            prefix = 'COM{}',
        elif os.name == 'posix':
            prefix = '/dev/ttyACM{}', '/dev/ttyUSB{}',

        for pref in prefix:
            for i in range(20):
                port = pref.format(i)
                try:
                    d = serial.Serial(port, timeout=0.2)
                    if d.write(self.START_STREAM):
                        d.close()
                        return port
                except:
                    continue

    # ----------------------------------------------------------------------
    def read(self, size):
        """Read size bytes from the serial port.

        Parameters
        ----------
        size : int
            Size of input buffer.

        Returns
        -------
        bytes
            Data readed.
        """

        return self.device.read(size)

    # ----------------------------------------------------------------------
    def write(self, data):
        """Output the given data over the serial port."""

        return self.device.write(data)

    # ----------------------------------------------------------------------
    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""

        self.device.reset_input_buffer()

    # ----------------------------------------------------------------------
    def reset_output_buffer(self):
        """Clear output buffer, aborting the current output and discarding all that is in the buffer. """
        self.device.reset_output_buffer()

    # ----------------------------------------------------------------------
    def close(self):
        """Close the serial communication."""

        self.device.close()


########################################################################
class CytonWiFi(Cyton):
    """
    This module implement a TCP connection using the WiFi module, this module
    was designed for works with se same syntax that `CytonRFDuino`.
    """

    STREAMING = False

    # ----------------------------------------------------------------------
    def __init__(self, ip_address, montage=None, local_ip_address=None, sample_rate='SAMPLE_RATE_1KHZ'):
        """WiFi mode connection.

        Parameters
        ----------
        ip_address: str.
            IP address with for WiFi module.
        montage: dictl, list, optional
            Decription of channels used.
        local_ip_address: str, optional.
            The IP for local machine.
        sample_rate: bytes, optional.
            The command for set the sample rate.

        """

        if not sample_rate in self.SAMPLE_RATE_VALUE.keys():
            sample_rate = getattr(self, sample_rate)
        # self.sample_rate_ = self.SAMPLE_RATE_VALUE[sample_rate]

        self.ip_address = ip_address
        self.stop_tcp_client()

        self.readed = None

        self.local_ip_address = local_ip_address
        if not self.local_ip_address:
            self.local_ip_address = self.get_local_ip_address()

        self.set_montage(montage)

        super().__init__()
        self.create_tcp_server()
        time.sleep(5)  # wait for the server
        self.start_loop()

        # self.start_tcp()

        atexit.register(self.close)
        self.command(sample_rate)

    # ----------------------------------------------------------------------
    def create_tcp_server(self):
        """Create TCP server.

        This server will handle the streaming EEG data.
        """
        self.local_wifi_server = WiFiShieldTCPServer(self.local_ip_address, self._data_serial)
        self.local_wifi_server_port = self.local_wifi_server.socket.getsockname()[1]
        logging.info(f"Opened socket on {self.local_ip_address}:{self.local_wifi_server_port}")

    # ----------------------------------------------------------------------
    def start_tcp_client(self):
        """Connect the board to the TCP server.

        Send configuration of the previous server created to the board, so they
        can connected to.
        """

        if self.ip_address is None:
            raise ValueError('self.ip_address cannot be None')

        logging.info(f"Init WiFi connection with IP: {self.ip_address}")

        self.requests_session = requests.Session()

        # requests.get(f"http://{self.ip_address}/yt")
        response = requests.get(f"http://{self.ip_address}/board")

        if response.status_code == 200:
            board_info = response.json()
            if not board_info['board_connected']:
                raise RuntimeError("No board connected to WiFi Shield.")

        res_tcp_post = requests.post(f"http://{self.ip_address}/tcp",
                                     json={
                                        'ip': self.local_ip_address,
                                        'port': self.local_wifi_server_port,
                                        'output': 'raw',
                                        'delimiter': False,
                                        'latency': 10,
                                         })
        if res_tcp_post.status_code == 200:
            tcp_status = res_tcp_post.json()
            if tcp_status['connected']:
                logging.info("WiFi Shield to Python TCP Socket Established")
            else:
                raise RuntimeWarning("WiFi Shield is not able to connect to local server.")

    # ----------------------------------------------------------------------
    def stop_tcp_client(self):
        """Stop TCP client."""
        requests.delete(f"http://{self.ip_address}/tcp")

    # ----------------------------------------------------------------------
    def get_local_ip_address(self):
        """Connect to internet for get the local IP."""

        try:
            local_ip_address = socket.gethostbyname(socket.gethostname())
            return local_ip_address
            # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # s.connect(("8.8.8.8", 80))
            # local_ip_address = s.getsockname()[0]
            # s.close()
            # return local_ip_address
        except Exception as e:
            logging.warning(f'{e}\nAssuming {DEFAULT_LOCAL_IP} as local ip address.')
            return DEFAULT_LOCAL_IP

    # ----------------------------------------------------------------------
    def write(self, data):
        """Send command to board through HTTP protocole."""

        if hasattr(data, 'decode'):
            data = data.decode()
        elif isinstance(data, int):
            data = chr(data)

        try:
            logging.info(f"Sending command: '{data}'")
            response = requests.post(f"http://{self.ip_address}/command", json={'command': data})
        except Exception as e:
            logging.info(f"Error on sending command '{data}': {e}")
            return

        if response.status_code == 200:
            self.readed = response.text
        elif response.status_code == 502:
            logging.info(f"No confirmation from board, does not mean fail.")
        else:
            logging.warning(f"Error code: {response.status_code} {response.text}")
            self.readed = None

    # ----------------------------------------------------------------------
    def read(self, size=None):
        """Read the response for some command.

        Not all command return response.
        """

        time.sleep(0.2)  # very important dealy for wait a response.
        return self.readed

    # ----------------------------------------------------------------------
    def close(self):
        """Stop TCP server."""

        if self.STREAMING:
            logging.warning(f"Closing.")
            self.STREAMING = False
            self.stop_collect()
            # self.stop_loop()
            asyncore.close_all()

    # ----------------------------------------------------------------------
    def start_loop(self):
        """Start the TCP server. """
        self.th_loop = Thread(target=asyncore.loop, args=(), )
        # self.th_loop = Process(target=asyncore.loop, args=())
        self.th_loop.start()

    # ----------------------------------------------------------------------
    def start_collect(self, milliseconds=1000, *args, **kwargs):
        """Start a data collection asynchronously.

        Send a command to the board for start the streaming through TCP.

        Parameters
        ----------
        milliseconds: int, optional
            The duration of data for packing.
        """

        self.reset_buffers()
        self.reset_input_buffer()
        self._start_streaming()
        # self._daisy = self.daisy()
        super().start_collect(*args, **kwargs)
        self.start_tcp_client()
        if milliseconds:
            self.pack_data(milliseconds=milliseconds)

    # ----------------------------------------------------------------------
    def stop_collect(self, *args, **kwargs):
        """Stop collecting data."""
        self.READING = False
        self._stop_streaming()

    # ----------------------------------------------------------------------
    def _start_streaming(self):
        """Start streaming."""

        if not self.STREAMING:
            response = requests.get(f"http://{self.ip_address}/stream/start")
            if response.status_code == 200:
                self.STREAMING = True
            else:
                logging.warning(f"Unable to start streaming.\nCheck API for status code {response.status_code} on /stream/start")

    # ----------------------------------------------------------------------
    def _stop_streaming(self):
        """Stop streaming."""

        if self.STREAMING:
            # self.stop_loop()
            response = requests.get(f"http://{self.ip_address}/stream/stop")
            if response.status_code == 200:
                self.STREAMING = False
            else:
                logging.warning(f"Unable to stop streaming.\nCheck API for status code {response.status_code} on /stream/start")

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

    # ----------------------------------------------------------------------
    def start(self):
        """This method does not action on WiFi mode."""
        pass

    # ----------------------------------------------------------------------
    def stop(self):
        """This method does not action on WiFi mode."""
        pass

    # ----------------------------------------------------------------------
    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""
        pass

    # ----------------------------------------------------------------------
    def reset_output_buffer(self):
        """Clear output buffer, aborting the current output and discarding all that is in the buffer. """
        pass


########################################################################
class WiFiShieldTCPServer(asyncore.dispatcher):
    """
    Simple TCP server.
    """

    SIZE = 32
    BUFFER = 10

    # ----------------------------------------------------------------------
    def __init__(self, host, data_queue):
        """Example function with types documented in the docstring.

        Parameters
        ----------
        host : str
            Local IP.
        data_queue : Queue
            Queue object for write stream data.

        """
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        self.set_reuse_addr()
        self.bind((host, 0))
        self.listen(1)
        self.data = data_queue

    # ----------------------------------------------------------------------
    def handle_accept(self):
        """Redirect the client connection."""
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logging.info(f'Incoming connection from {addr}')
            self.handler = asyncore.dispatcher_with_send(sock)
            self.handler.handle_read = self._handle_read
            self.handler.handle_error = self._handle_error

    # ----------------------------------------------------------------------
    def _handle_read(self):
        """Write the input streaming into the Queue object."""
        self.data.extend(self.handler.recv(33 * 90))

    # ----------------------------------------------------------------------
    def _handle_error(self):
        """"""
        # I'm feeling dirty for this "solution"
