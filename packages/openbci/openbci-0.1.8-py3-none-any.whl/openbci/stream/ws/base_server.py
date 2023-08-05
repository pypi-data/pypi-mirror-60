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

import json
import traceback
import logging

# from tornado.ioloop import IOLoop
from tornado import websocket
# from datetime import timedelta

from openbci import acquisition

from tornado import gen
# import numpy as np


########################################################################
class __WebSocketHandler(websocket.WebSocketHandler):
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
    # @gen.coroutine
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
        except Exception as e:
            pass

        except:
            pass


    # ----------------------------------------------------------------------
    @gen.coroutine
    def timed_stream(self):
        """Prepare package for send it via ws."""


        # if self.STATUS["CLIENTS"] and self.STATUS["STREAMING"]:
            # # pass
            # # If clients connected call again.
            # # IOLoop.instance().add_timeout(timedelta(seconds=0.1), self.timed_stream)
            # IOLoop.instance().call_later(0.1, self.timed_stream)
        # else:
            # # If no clients stop streamming
            # if not self.STATUS["CLIENTS"]:
                # logging.warning('No clients!!')
            # elif not self.STATUS["STREAMING"]:
                # logging.warning('No streamming!!')
            # self.STATUS["STREAMING"] = False
            # self.stop_stream()
            # return

        # if pack_size := self.bci_device.eeg_pack.qsize():
            # # return

            # data = {
                # 'type': 'STREAM',
                # 'pack_id': self.STATUS["PACK_ID"],
                # 'buffer_eeg': self.bci_device.eeg_buffer.qsize(),
                # 'buffer_pack': pack_size - 1,
                # 'buffer_serial': len(self.bci_device.eeg_serial),
            # }

            # if not self.STATUS["CLEANED"] and self.STATUS["PACK_ID"] == 0:
                # self.bci_device.reset_buffers()
                # # self.STATUS["PACK_ID"] = 0
                # self.STATUS["CLEANED"] = False

            # data['data'] = [d.tolist() for d in self.bci_device.eeg_pack.get()]
            # self.send_data(data)
            # self.STATUS["PACK_ID"] += 1




        while self.STATUS["CLIENTS"] and self.STATUS["STREAMING"]:
            # pass
            # If clients connected call again.
            # IOLoop.instance().add_timeout(timedelta(seconds=0.1), self.timed_stream)
            # IOLoop.instance().call_later(0.1, self.timed_stream)

            if pack_size := self.bci_device.eeg_pack.qsize():

                if pack_size > 2:
                    self.bci_device.eeg_pack.get()

                data = {
                    'type': 'STREAM',
                    'pack_id': self.STATUS["PACK_ID"],
                    'buffer_eeg': self.bci_device.eeg_buffer.qsize(),
                    'buffer_pack': self.bci_device.eeg_pack.qsize() - 1,
                    # 'buffer_serial': len(self.bci_device.eeg_serial),
                }

                if not self.STATUS["CLEANED"] and self.STATUS["PACK_ID"] == 0:
                    self.bci_device.reset_buffers()
                    # self.STATUS["PACK_ID"] = 0
                    self.STATUS["CLEANED"] = False
                    yield


                # dta = []
                # for _ in range(pack_size):
                    # dta.append([d.tolist() for d in self.bci_device.eeg_pack.get()])
                # dta = np.array(dta)
                # data['data'] = [np.concatenate(dta[:, i]).tolist() for i in range(dta.shape[1])]

                data['data'] = [d.tolist() for d in self.bci_device.eeg_pack.get()]

                self.send_data(data)
                self.STATUS["PACK_ID"] += 1

                yield

            yield


        # If no clients stop streamming
        if not self.STATUS["CLIENTS"]:
            logging.warning('No clients!!')
        elif not self.STATUS["STREAMING"]:
            logging.warning('No streamming!!')

        self.stop_stream()
        return




########################################################################
class __WSHandler(__WebSocketHandler):
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
    def register(self, device_id, **kwargs):
        """"""
        if device_id in self.STATUS['DEVICES']:
            # self.device_id = device_id
            logging.info(f"Client {self} registered for {device_id} device")

        else:
            logging.warning(f"No device {device_id} attached.")
            self.set_up(device_id, **kwargs)


    # ----------------------------------------------------------------------
    def start_stream(self, milliseconds, boardmode=None):
        """Start streamming in device with selected boardmode,"""

        if (not self.STATUS["STREAMING"]):# or (not self.bci_device is None):
            self.STATUS["STREAMING"] = True
            if boardmode:
                self.bci_device.command(getattr(self.bci_device, boardmode))
            self.bci_device.start_collect(milliseconds=milliseconds)

            logging.warning('Start streamming')
            self.timed_stream()
            # self.timed_stream_callback = PeriodicCallback(self.timed_stream, callback_time=milliseconds, jitter=0.1)
            # self.timed_stream_callback.start()
        else:
            logging.warning('Already streamming')
            self.stop_stream()
            self.start_stream(milliseconds, boardmode)

    # ----------------------------------------------------------------------
    def stop_stream(self, **request):
        """Stop streamming in device."""

        self.STATUS["STREAMING"] = False
        logging.warning('Stop streamming')
        self.bci_device.stop_collect()
        # self.timed_stream_callback.stop()


########################################################################
class WSHandler_Serial(__WSHandler):
    """`bci_device` is created explicitly.

    This means that RFduino must be placed before start the system.
    """

    # ----------------------------------------------------------------------
    def set_up(self, device_id=None, montage=None, sample_rate='SAMPLE_RATE_250HZ'):
        """"""
        if device_id in self.STATUS['DEVICES']:
            bci_device = self.STATUS['DEVICES'][device_id]
            bci_device.close()

        try:
            bci_device = acquisition.CytonRFDuino(device_id, montage, sample_rate)
            self.STATUS['DEVICES'][device_id] = bci_device
            self.device_id = device_id
            logging.info(f"Client {self} registered for {device_id} device")

        except:
            logging.warning(f"No device attached: {e}")


########################################################################
class WSHandler_WiFi(__WSHandler):
    """`bci_device` is created explicitly.

    This means that WiFi shield must be connected to the AP or network.

    """
    # ----------------------------------------------------------------------
    def set_up(self, device_id, montage=None, local_ip_address=None, sample_rate='SAMPLE_RATE_250HZ'):
        """"""
        if device_id in self.STATUS['DEVICES']:
            bci_device = self.STATUS['DEVICES'][device_id]
            bci_device.close()

        try:
            bci_device = acquisition.CytonWiFi(device_id, montage, sample_rate)
            self.STATUS['DEVICES'][device_id] = bci_device
            self.device_id = device_id
            logging.info(f"Client {self} registered for {device_id} device")

        except Exception as e:
            logging.warning(f"No device attached: {e}")

