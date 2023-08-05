import netifaces
import requests
import nmap
from tornado.web import RequestHandler
from openbci.utils.scan_wifi_modules import scan


########################################################################
class HomeHandler(RequestHandler):
    """"""

    # -------------------------------------------------------------------
    def get(self):
        """"""
        self.render('html/home.html')


########################################################################
class EndPointHandler(RequestHandler):

    # ----------------------------------------------------------------------
    def get(self):
        """"""
        command = self.get_argument('command')
        response = getattr(self, f"command_{command}")()
        self.write(response)

    # ----------------------------------------------------------------------
    def command_scan(self):
        """"""
        boards = {}

        for interface in netifaces.interfaces():

            if not (interface.startswith("wlan") or interface.startswith("wlp")):
                continue

            local_lan = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            nm = nmap.PortScanner()
            nm.scan(hosts=f'{local_lan}/24', arguments='-sn')
            hosts = nm.all_hosts()

            for host in hosts:
                try:
                    response = requests.get(f'http://{host}/board', timeout=0.1)
                    if response.ok:
                        boards[host] = response.json()
                except:
                    continue

        return boards


