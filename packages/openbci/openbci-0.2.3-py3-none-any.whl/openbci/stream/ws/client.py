"""
=========
WS Server
=========

A Python client for access to WebSocket streammed data.
"""

import sys
import json
import logging
import numpy as np
from datetime import datetime

from socket import error as socket_error
from abc import ABCMeta, abstractmethod
import time

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect

from multiprocessing import Process, Manager, Queue
from queue import Queue as ClassicQueue


# MARKERS = Queue(maxsize=1)
# FINISH = Queue(maxsize=1)
MARKERS = Manager().Queue(maxsize=1)
FINISH = Manager().Queue(maxsize=1)


########################################################################
class WSClient(metaclass=ABCMeta):
    """Base client for headwares implementations.

    This class just connect with server and redirect the data flow.
    """

    # ----------------------------------------------------------------------
    def start(self, ip, device_id, port, mode='wifi', pack_size=1000, boardmode='BOARD_MODE_MARKER', sample_rate='SAMPLE_RATE_1KHZ', montage=None, force=False):
        """Try to connect with the WebSocket server.

        On WebSocket mode the acquisition only works with package data.

        Parameters
        ----------
        ip : str
            Is the IP where run WebSocket the server.
        port : str
            The port for the WebSocket server.
        mode: str, optional
            The board mode must be specified explicitly, the options are:
            `serial` and `wifi` (default).
        pack_size : int, optional
            Milliseconds for packs.
        boardmode : str, optional
            The boardmode, one of `BOARD_MODE_DEFAULT`, `BOARD_MODE_DEBUG`,
            `BOARD_MODE_ANALOG`, `BOARD_MODE_DIGITAL`, `BOARD_MODE_MARKER` or
            `BOARD_MODE_GET`.
        """

        self.url = f'ws://{ip}:{port}/{mode}'
        self.ioloop = IOLoop.instance()

        self.connect()
        self.port = port
        self.ip = ip
        self.pack_size = pack_size
        self.boardmode = boardmode
        self.sample_rate_ = sample_rate
        self.device_id = device_id
        self.montage = montage
        self.force = force

        self.ioloop.start()

    # # ----------------------------------------------------------------------
    # @gen.coroutine
    # def _check_markers(self):
        # """"""
        # logging.warning("MMM")
        # while not FINISH.qsize():
            # pass
            # logging.warning("W")
            # if MARKERS.qsize():
                # logging.warning("MARKER")
                # marker, burst = MARKERS.get()
                # yield self.ws.write_message(json.dumps({'command': 'send_marker', 'kwargs': {'marker': marker, 'burst': 4, }, }))
            # time.sleep(0.001)

    # ----------------------------------------------------------------------
    def __getattr__(self, attr):
        """For call remote methods with local syntax.

        The WebSocket server consist in a set of methods that can be called with
        a JSON structure, for example `start_stream`, this method need
        `boardmode` and `milliseconds` arguments`, the WebSocket message must be
        costructed as:

        >>> message = "{'command':'start_stream','kwargs':{'boardmode':'BOARD_MODE_MARKER','milliseconds':1000}}"
        >>> self.ws.write_message(message)

        for prevent this unfamiliar structure, this method add a Python like
        syntax:

        >>> self.start_stream(boardmode='BOARD_MODE_MARKER', milliseconds=1000)

        even if the `start_stream` method is not explicitly defined.


        Parameters
        ----------
        attr : str
            Funtion name

        Returns
        -------
        function
            Artificial function that send a request to the WebSocket.
        """

        def inset(**kwargs):
            self.ws.write_message(json.dumps({'command': attr, 'kwargs': kwargs, }))
        return inset

    # ----------------------------------------------------------------------
    @gen.coroutine
    def connect(self):
        """Try connection with server.

        The streamming will start automatically.

        Returns
        -------
        bool
            `True` if coonected, otherwise `False`.
        """

        logging.info(f"Trying connection to...")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception as e:
            logging.error(f"Connection error:{self.url}, {e}")
            sys.exit()
        else:
            logging.info(f"Connected to {self.url}")
            self._run()
            # self._check_markers()

    # ----------------------------------------------------------------------
    @gen.coroutine
    def _run(self):
        """Start the data streamming.

        This method will call a `callback` method on each received message.
        """

        if self.force:
            self.set_up(device_id=self.device_id, sample_rate=self.sample_rate_, montage=self.montage)
        else:
            self.register(device_id=self.device_id, sample_rate=self.sample_rate_, montage=self.montage)
        self.start_stream(milliseconds=self.pack_size, boardmode=self.boardmode)

        while not FINISH.qsize():

            if MARKERS.qsize():
                marker, burst = MARKERS.get()
                # logging.warning(f"MARKER: {marker} {burst}")
                yield self.ws.write_message(json.dumps({'command': 'send_marker', 'kwargs': {'marker': marker, 'burst': burst, }, }))

            data = yield self.ws.read_message()

            if not data:
                logging.warning(f'No data in pack')
                logging.warning(f'{data}')
                continue

            data = json.loads(data)

            if not 'data' in data:
                continue

            self.callback(data)

        yield self.ws.write_message(json.dumps({'command': 'stop_stream', 'kwargs': {}, }))
        self.close()

    # ----------------------------------------------------------------------
    def close(cls):
        ioloop = IOLoop.current()
        ioloop.add_callback(ioloop.stop)

    # ----------------------------------------------------------------------
    @abstractmethod
    def callback(self, data):
        """Callback method for each data package.

        Parameters
        ----------
        data : dict
            The packaged deserialized data from headware.
        """
        pass


########################################################################
class _CytonWS(WSClient):
    """Use `WSClient` for redirect the data to a Queue."""

    # ----------------------------------------------------------------------
    def __init__(self, ip, device_id, port=8845, mode='wifi', queue=None, pack_size=1000, boardmode='BOARD_MODE_MARKER', callback=None, sample_rate='SAMPLE_RATE_1KHZ', montage=[], force=False):
        """Example function with types documented in the docstring.

        `PEP 484`_ type annotations are supported. If attribute, parameter, and
        return types are annotated according to `PEP 484`_, they do not need to be
        included in the docstring:

        Parameters
        ----------
        ip : str
            Is the IP where run WebSocket the server.
        port : str
            The port for the WebSocket server.
        mode: str, optional
            The board mode must be specified explicitly, the options are:
            `serial` and `wifi` (default).
        pack_size : int, optional
            Milliseconds for packs.
        boardmode : str, optional
            The boardmode, one of `BOARD_MODE_DEFAULT`, `BOARD_MODE_DEBUG`,
            `BOARD_MODE_ANALOG`, `BOARD_MODE_DIGITAL`, `BOARD_MODE_MARKER` or
            `BOARD_MODE_GET`.
        queue : queue, ooptional
             If a queue is provided the system will use it, otherwise a new one
             will be created.
        """

        if queue:
            self._eeg_pack = queue
        else:
            self._eeg_pack = Manager().Queue()

        self._eeg_buffer = Manager().Queue()

        if callback:
            self.callback = callback
        else:
            logging.info("No callback function defined!!")

        self._start_collect = lambda pack_size = 1000: self.start(ip, device_id, port, mode, pack_size, boardmode, sample_rate, montage, force)

    # ----------------------------------------------------------------------
    def start_collect(self, pack_size=1000):
        """"""
        self._start_collect(pack_size)

    # ----------------------------------------------------------------------
    def start_collect_process(self, pack_size=1000):
        """"""
        self.collect_process = Process(target=self._start_collect, args=(pack_size, ))
        self.collect_process.start()

    # ----------------------------------------------------------------------
    def stop_collect_process(self):
        """"""
        FINISH.put("dummy")
        self.collect_process.terminate()
        self.collect_process.join()
        self.dump_queues()

    # ----------------------------------------------------------------------
    @property
    def eeg_pack(self):
        """property handler for the main queue."""

        return self._eeg_pack

    # ----------------------------------------------------------------------
    @property
    def eeg_buffer(self):
        """"""
        return self._eeg_buffer

    # ----------------------------------------------------------------------
    def dump_queues(self):
        """"""
        _eeg_pack = ClassicQueue()
        _eeg_buffer = ClassicQueue()

        while self._eeg_pack.qsize():
            _eeg_pack.put(self._eeg_pack.get())

        while self._eeg_buffer.qsize():
            _eeg_buffer.put(self._eeg_buffer.get())

        self._eeg_buffer = _eeg_buffer
        self._eeg_pack = _eeg_pack

    # ----------------------------------------------------------------------
    # @gen.coroutine

    def callback(self, data):
        """Callback method for each data package.

        Add the input data to the queue.

        Parameters
        ----------
        data : dict
            The packaged deserialized data from headware.
        """

        self._eeg_pack.put(np.array(data['data']).T)

        for d in np.array(data['data']).T:
            self._eeg_buffer.put(d)

    # ----------------------------------------------------------------------
    @property
    def sample_rate(self):
        """"""
        if self.eeg_buffer.qsize() > 2:
            eeg = np.array(self.eeg_buffer.queue)
            sr = eeg.shape[0] / (datetime.fromtimestamp(eeg[-1][4]) - datetime.fromtimestamp(eeg[0][4])).total_seconds()
            del eeg
            return sr

        if self.eeg_pack.qsize() >= 2:
            eeg = np.array(self.eeg_pack.queue)[-1]
            sr = eeg.shape[0] / (datetime.fromtimestamp(eeg[-1][4]) - datetime.fromtimestamp(eeg[0][4])).total_seconds()
            del eeg
            return sr

        else:
            logging.warning(f"Not enough data for calculate the sample frequency.")


########################################################################
class CytonWS_dummy:

    # ----------------------------------------------------------------------
    def __init__(self, ws):
        # self.marker = None
        self._eeg_pack = Queue()
        self.ws = ws

    # ----------------------------------------------------------------------
    @property
    def eeg_pack(self):
        """"""
        return self._eeg_pack

    # ----------------------------------------------------------------------
    def close(cls):
        ioloop = IOLoop.current()
        ioloop.add_callback(ioloop.stop)

    # ----------------------------------------------------------------------
    def send_marker(self, marker, burst=4):
        """"""
        if not MARKERS.qsize():
            MARKERS.put((marker, burst))

########################################################################


class CytonWS:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, ip, device_id, port=8845, mode='wifi', queue=None, pack_size=1000, boardmode='BOARD_MODE_MARKER', callback=None, sample_rate='SAMPLE_RATE_1KHZ', montage=[], force=False):
        """Constructor"""

        self.openbci = _CytonWS(ip, device_id, port=port, mode=mode, queue=queue, pack_size=pack_size, boardmode=boardmode, callback=callback, sample_rate=sample_rate, montage=montage, force=force)

    # ----------------------------------------------------------------------
    # def collect(self, t1, /, wait=True):
    def collect(self, t1, wait=True):
        """"""
        self.start_collect()
        if wait:
            self.wait_for_data()
        time.sleep(t1)
        self.openbci.stop_collect_process()

    # ----------------------------------------------------------------------
    def wait_for_data(self):
        """"""
        logging.info("Waiting for data...")
        while not self.openbci.eeg_pack.qsize():
            time.sleep(0.1)
        logging.info("Stream started.")

    # ----------------------------------------------------------------------
    def start_collect(self):
        """"""
        self.openbci.start_collect_process()

    # ----------------------------------------------------------------------
    def stop_collect(self):
        """"""
        self.openbci.stop_collect_process()

    # ----------------------------------------------------------------------
    def send_marker(self, marker, burst=4):
        """"""
        if not MARKERS.qsize():
            MARKERS.put((marker, burst))

    # ----------------------------------------------------------------------
    def __getattr__(self, attr):
        """"""

        if hasattr(self.openbci, attr):
            return getattr(self.openbci, attr)


# ----------------------------------------------------------------------
def CytonWS_decorator(ip, device_id, port=8845, mode='wifi', queue=None, pack_size=1000, boardmode='BOARD_MODE_MARKER', sample_rate='SAMPLE_RATE_1KHZ', montage=[], force=False):

    def wrapper(fn):
        def my_callback(data):
            fn(_ws, data)

        ws = _CytonWS(ip, device_id, port, mode, pack_size=pack_size, boardmode=boardmode, callback=my_callback, sample_rate=sample_rate, montage=montage, force=force)
        _ws = CytonWS_dummy(ws)
        ws._eeg_pack = _ws.eeg_pack
        ws.start_collect()

    return wrapper
