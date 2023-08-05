# import psutil
import logging

from openbci.stream.ws.server import create_server
from openbci.utils import autokill_process

autokill_process()
# from openbci.acquisition import Cyton

# threading.stack_size(2**26)
# sys.setrecursionlimit(2**20)

logging.getLogger().setLevel(logging.INFO)
logging.info(f"EEGSTREAM started.")


# minimal configuration
config = {
    'websocket_port': 8845,
    # 'shield_wifi_ip': '192.168.1.113',
    # 'sample_rate': Cyton.SAMPLE_RATE_1KHZ,
    # 'sample_rate': Cyton.SAMPLE_RATE_250HZ,
    # 'sample_rate': Cyton.SAMPLE_RATE_500HZ,
}


# ----------------------------------------------------------------------
def run():
    create_server(config)


if __name__ == '__main__':
    run()

