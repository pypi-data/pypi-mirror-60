"""
===========
HTTP Server
===========

Tornado HTTP server with a WebSocket running in it, it is composed of:

  * **Application**: A collection of request handlers that make up a web application.
  * **HTTPServer**: A non-blocking, single-threaded HTTP server.
"""

from threading import Thread
# from multiprocessing import Process
import logging
import os

try:
    from .app import EndPointHandler, HomeHandler
    from .base_server import WSHandler_Serial, WSHandler_WiFi
except:
    from app import EndPointHandler, HomeHandler
    from base_server import WSHandler_Serial, WSHandler_WiFi

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, url

# from .base_server import WSHandler_Serial, WSHandler_WiFi

DEBUG = True
STATIC_DIRNAME = "static"


# ----------------------------------------------------------------------
def make_app(config):
    """A collection of request handlers that make up a web application.

    Parameters
    ----------
    config: dict
        Object with configurations from main window.

    Returns
    -------
    Application
        A collection of request handlers that make up a web application.
    """

    settings = {
        'debug': DEBUG,
        # 'static_path': config.get('user_dir', '.'),
        # 'static_url_prefix': '/download/',  # The static file handler is used for access/download generated files.
        'xsrf_cookies': False,


        "static_path": os.path.join(os.path.dirname(__file__), STATIC_DIRNAME),
        "static_url_prefix": "/static/",



    }

    config['download'] = 'http://localhost:{}{}'.format(config['websocket_port'], settings['static_url_prefix'])

    # if config.get('shield_wifi_ip', False):
        # os.environ['IP_WIFI'] = config['shield_wifi_ip']

    # if config.get('sample_rate', False):
        # os.environ['SAMPLE_RATE'] = config['sample_rate'].decode()

    return Application([

        url(r'^/', HomeHandler),
        url(r'^/api', EndPointHandler),

        url(r'^/wifi', WSHandler_WiFi, {'bci_config': config, }),
        url(r'^/serial', WSHandler_Serial, {'bci_config': config, }),

    ], **settings)


# ----------------------------------------------------------------------
def create_server(config):
    """Entry point for invote the Websocket from main window.

    Parameters
    ----------
    config: dict
        Object with configurations from main window.

    Returns
    -------
    HTTPServer
        Server object that can be stoped in the main window.
    """

    port = int(config['websocket_port'])

    logging.info("OpenBCI server running on port {}".format(port))
    application = make_app(config)
    # asyncio.set_event_loop(asyncio.new_event_loop())
    http_server = HTTPServer(application)

    try:
        http_server.listen(port)
    except:
        pass

    # IOLoop.instance().start()

    if hasattr(IOLoop.instance(), 'asyncio_loop'):

        # Start new IOLoop only if previous is dead or not exist
        if not IOLoop.instance().asyncio_loop.is_running():
            try:
                # Using a tthread for keep main window alive
                # IOLoop.instance().start()
                Thread(target=IOLoop.instance().start, args=()).start()
                # Process(target=IOLoop.instance().start, args=()).start()
            except:
                pass  # TODO: Windows test

    else:  # Sometimes this instance ('asyncio_loop') not exist in windows.
        Thread(target=IOLoop.instance().start, args=()).start()
        # Process(target=IOLoop.instance().start, args=()).start()

    return http_server  # returning server to main window


# ----------------------------------------------------------------------
def stop_websocket_server():
    """Try to stop server.

    `Try` means that the task will be released to OS.
    """

    ioloop = IOLoop.current()
    ioloop.add_callback(ioloop.stop)


if __name__ == '__main__':

    config = {
        'websocket_port': 8845,
        'user_dir': '.',
    }
    create_server(config)
