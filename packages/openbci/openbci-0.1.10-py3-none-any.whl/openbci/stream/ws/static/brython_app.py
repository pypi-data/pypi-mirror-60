from browser import document
from radiant import WebSocket, get
import json

########################################################################


class OpenBCI(WebSocket):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, ip, ip_wifi, latency):
        """"""
        self.ip_wifi = ip_wifi
        self.latency = latency

        self.stream_id = document.select_one('#stream-id')
        # self.serial_buffer = document.select_one('#stream-serial_buffer')
        self.eeg_buffer = document.select_one('#stream-eeg_buffer')
        self.eeg_pack = document.select_one('#stream-eeg_pack')

        super().__init__(ip)

    # ----------------------------------------------------------------------
    def on_open(self, evt):
        """"""
        data = {"command": "set_up",
                'kwargs': {"device_id": self.ip_wifi,
                           "sample_rate": 'SAMPLE_RATE_250HZ',
                           }
                }

        self.send(data)

        data = {'command': 'start_stream',
                'kwargs': {'milliseconds': int(self.latency),
                           'boardmode': 'BOARD_MODE_MARKER',
                           }
                }

        self.send(data)

    # ----------------------------------------------------------------------
    def on_message(self, evt):
        """"""

        try:
            data = json.loads(evt.data[:300] + "]]}")
            # print(data.values())
            # print(data['pack_id'])
            self.stream_id.html = str(data['pack_id'])
            # self.serial_buffer.html = str(data['buffer_serial'])
            self.eeg_buffer.html = str(data['buffer_eeg'])
            self.eeg_pack.html = str(data['buffer_pack'])
        except:
            pass

        # print("Message received: {}".format(evt.data[:300]))

        # print(data['pack_id'])


########################################################################
class OpenBCI_API:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        self.openbci = None

        self.button_connect = document.select_one("#btn-connect")
        self.button_connect.bind('click', self.connect)

        self.button_stop = document.select_one("#btn-stop")
        self.button_stop.bind('click', self.stop)

    # ----------------------------------------------------------------------
    def connect(self, evt):
        """"""
        self.ip_rasp = document.select_one('#input-ip_rasp')
        self.ip_wifi = document.select_one('#input-ip_wifi')
        self.latency = document.select_one('#input-latency')

        self.openbci = OpenBCI(f"ws://{self.ip_rasp.value}:8845/wifi", self.ip_wifi.value, self.latency.value)

        self.button_connect.style = {'display': 'none'}
        self.button_stop.style = {'display': 'block'}

        self.ip_rasp.attrs['disabled'] = True
        self.ip_wifi.attrs['disabled'] = True
        self.latency.attrs['disabled'] = True

    # ----------------------------------------------------------------------
    def stop(self, evt):
        """"""
        if self.openbci:
            self.openbci.close_connection()

        self.button_connect.style = {'display': 'block'}
        self.button_stop.style = {'display': 'none'}

        del self.ip_rasp.attrs['disabled']
        del self.ip_wifi.attrs['disabled']
        del self.latency.attrs['disabled']

