"""
=========
WSHandler
=========

WebSockets are not standard HTTP connections. The "handshake" is HTTP,
but after the handshake, the protocol is message-based.

This implementation suppose that input message are in JSON format, each input
message will trigger a response message (in JSON format too) with a ``type``
information.
"""

import os
from io import StringIO
import time
import json
import traceback
import logging

from tornado.ioloop import IOLoop
from tornado import websocket
from datetime import timedelta

from openbci import acquisition
from openbci.database import load_sample_8ch_bin


# ########################################################################
# class WsClient:
    # """"""

    # # ----------------------------------------------------------------------
    # def __init__(self, client):
        # """Constructor"""

        # self.client = client

    # # ----------------------------------------------------------------------
    # def set_device(self, device):
        # """"""
        # self.bci_device = device


########################################################################
class WebSocketHandler(websocket.WebSocketHandler):
    """"""

    # ----------------------------------------------------------------------
    def initialize(self, bci_config):
        """Load config values from main app.

        Parameters
        ----------
        bci_config: dict
            Dictionary from runner.
        """

    # ----------------------------------------------------------------------
    def check_origin(self, origin):
        """Prevents a WebSocket from being used by another website that the user is also visiting."""
        return True

    # ----------------------------------------------------------------------
    def open(self, *args, **kwargs):
        """Return a message to client for confirm connection."""

        logging.warning(f'Adding client {self}')
        self.STATUS["CLIENTS"].append(self)

    # ----------------------------------------------------------------------
    def on_close(self):
        """Remove client from stream."""

        if self in self.STATUS["CLIENTS"]:
            self.STATUS["CLIENTS"].pop(self.STATUS["CLIENTS"].index(self))
        logging.info(f"Removing client {self}")

    # ----------------------------------------------------------------------
    @property
    def bci_device(self):
        """"""
        if hasattr(self, 'device_id'):
            return self.STATUS['DEVICES'][self.device_id]
        else:
            return None

    # ----------------------------------------------------------------------
    def on_message(self, message):
        """Process input message.

        Parameters
        ----------
        message: dict
            Dictionary with 'command' key as python method.
        """

        if not self in self.STATUS["CLIENTS"]:
            return

        request = json.loads(message)

        if not request.get('command', False):
            error = f'No argument "command" in this request./nmessage: {message}'
            logging.warning(error)
            self.send_data({'type': 'ERROR', 'message': error}, request)
            return

        command = request.get('command')
        kwargs = request.get('kwargs')

        if getattr(self.bci_device, command, False):  # command is a method
            try:
                logging.info("Running command: \"{}\"".format(command))
                response = getattr(self.bci_device, command)(**kwargs)  # call method
                self.send_data({'type': 'COMMAND', 'command': command, 'response': str(response), }, request)
            except AttributeError as e:
                t = {}
                t['message'] = str(e)
                t['traceback'] = traceback.format_exc()
                self.send_data({'type': 'ERROR', 'message': t, }, request)

        elif getattr(self, command, False):  # command is a method
            try:
                logging.info("Running command: \"{}\"".format(command))
                getattr(self, command)(**kwargs)  # call method
            except AttributeError as e:
                t = {}
                t['message'] = str(e)
                t['traceback'] = traceback.format_exc()
                self.send_data({'type': 'ERROR', 'message': t, }, request)
        else:
            self.send_data({'type': 'ERROR', 'message': 'No argument "command" in this request.', }, request)

    # ----------------------------------------------------------------------
    def send_data(self, data, request={}):
        # global STREAMING, CLIENTS
        """Return data to client.

        Parameters
        ----------
        data: dict
            Dictionary with desired data to return.
        request: dict
            Dictionary with request parameters, like command.
        """

        try:  # send data to client
            for client in self.STATUS["CLIENTS"]:
                client.write_message(data)
            logging.info(f'Writing data {data.get("pack_id", "")} for {len(self.STATUS["CLIENTS"])} clients, {data["buffer_pack"]}')
        # except websocket.WebSocketClosedError as e:
            # logging.warning("Send data: ", e)
            # pass
        except Exception as e:
            pass

        except:
            pass

    # ----------------------------------------------------------------------
    def timed_stream(self):
        """Prepare package for send it via ws."""

        if self.STATUS["CLIENTS"] and self.STATUS["STREAMING"]:
            # If clients connected call again.
            IOLoop.instance().add_timeout(timedelta(seconds=0.1), self.timed_stream)
        else:
            # If no clients stop streamming
            if not self.STATUS["CLIENTS"]:
                logging.warning('No clients!!')
            elif not self.STATUS["STREAMING"]:
                logging.warning('No streamming!!')
            self.STATUS["STREAMING"] = False
            self.stop_stream()
            return

        data = {
            'type': 'STREAM',
            'pack_id': self.STATUS["PACK_ID"],
            'buffer_eeg': self.bci_device.eeg_buffer.qsize(),
            'buffer_pack': self.bci_device.eeg_pack.qsize() - 1,
            'buffer_serial': len(self.bci_device.eeg_serial),
            # 'buffer_serial': self.bci_device.eeg_serial.qsize(),
            # 'sample_rate': self.bci_device.sample_rate,
        }

        if not self.STATUS["CLEANED"] and self.STATUS["PACK_ID"] == 0:
            self.bci_device.reset_buffers()
            # self.STATUS["PACK_ID"] = 0
            self.STATUS["CLEANED"] = False

        # if pack is available
        if data['buffer_pack']:
            data['data'] = [d.tolist() for d in self.bci_device.eeg_pack.get()]
            # Sample rate is calculated for each package
            # data['sample_rate'] = len(data['data'][2]) / (self.bci_device.pack_time * 1e-3)
            self.send_data(data)
            # print(elf.STATUS["PACK_ID"])
            self.STATUS["PACK_ID"] += 1
            # self.STATUS["PACK_ID"] = self.STATUS["PACK_ID"] % 2 ** 10


########################################################################
class WSHandler(WebSocketHandler):
    """Websocket handler."""

    # Attributes in a mutable object.
    STATUS = dict(

        CLIENTS=[],
        STREAMING=False,
        PACK_ID=-5,
        CLEANED=False,
        DEVICES={},

    )

    # ----------------------------------------------------------------------
    # def start_stream(self, **request):
    def start_stream(self, milliseconds, boardmode=None):
        """Start streamming in device with selected boardmode,"""

        if not self.STATUS["STREAMING"]:
            logging.warning('Start streamming')
            self.STATUS["STREAMING"] = True
            if boardmode:
                self.bci_device.command(getattr(self.bci_device, boardmode))
            self.bci_device.start_collect(milliseconds=milliseconds)

            self.timed_stream()
        else:
            logging.warning('Already streamming')

    # ----------------------------------------------------------------------
    def stop_stream(self, **request):
        """Stop streamming in device."""

        self.STATUS["STREAMING"] = False
        logging.warning('Stop streamming')
        self.bci_device.stop_collect()

    # ----------------------------------------------------------------------
    def register(self, device_id, **kwargs):
        """"""
        if device_id in self.STATUS['DEVICES']:
            self.device_id = device_id
            logging.info(f"Client {self} registered for {device_id} device")

        else:
            logging.warning(f"No device {device_id} attached.")
            self.set_up(device_id, **kwargs)


# ########################################################################
# class WSHandler_Serial(WSHandler):
    # """`bci_device` is created explicitly.

    # This means that RFduino must be placed before start the system.
    # """
    # try:
        # bci_device = acquisition.CytonRFDuino()
    # except:
        # # logging.warning(str(e))
        # logging.warning("No Serial device attached, websocket will not work")
        # pass


# ########################################################################
# class WSHandler_WiFi(WSHandler):
    # """`bci_device` is created explicitly.

    # This means that WiFi shield must be connected to the AP or network.
    # """
    # try:
        # bci_device = acquisition.CytonWiFi(os.environ.get('IP_WIFI', '192.168.1.185'),
                                           # sample_rate=os.environ.get('SAMPLE_RATE', str(acquisition.Cyton.SAMPLE_RATE_1KHZ)).encode())
    # except Exception as e:
        # logging.warning(f"No Wifi device attached, websocket will not work:\n{e}")
        # pass


########################################################################
class WSHandler_Serial(WSHandler):
    """`bci_device` is created explicitly.

    This means that RFduino must be placed before start the system.
    """

    # ----------------------------------------------------------------------
    def set_up(self, device_id=None, montage=None, file=None, timeout=0.5, write_timeout=0.1, sample_rate='SAMPLE_RATE_250HZ'):
        """"""
        if device_id in self.STATUS['DEVICES']:
            bci_device = self.STATUS['DEVICES'][device_id]
            bci_device.close()

        try:
            bci_device = acquisition.CytonRFDuino(device_id, montage, file, timeout, write_timeout, sample_rate)
            self.STATUS['DEVICES'][device_id] = bci_device
            self.device_id = device_id
            logging.info(f"Client {self} registered for {device_id} device")

        except:
            logging.warning("No Serial device attached")


########################################################################
class WSHandler_WiFi(WSHandler):
    """`bci_device` is created explicitly.

    This means that WiFi shield must be connected to the AP or network.

    """

    # ----------------------------------------------------------------------
    def set_up(self, device_id, montage=None, local_ip_address=None, sample_rate='SAMPLE_RATE_1KHZ'):
        """"""
        if device_id in self.STATUS['DEVICES']:
            bci_device = self.STATUS['DEVICES'][device_id]
            bci_device.close()

        try:
            bci_device = acquisition.CytonWiFi(device_id, montage, local_ip_address, sample_rate)
            self.STATUS['DEVICES'][device_id] = bci_device
            self.device_id = device_id
            logging.info(f"Client {self} registered for {device_id} device")

        except Exception as e:
            logging.warning(f"No WiFi device attached: {e}")

