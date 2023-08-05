import psutil
import os
import logging
import atexit
import signal
import sys
import threading

from openbci.stream.ws.server import create_server
# from openbci.acquisition import Cyton

# threading.stack_size(2**26)
# sys.setrecursionlimit(2**20)

logging.getLogger().setLevel(logging.INFO)
logging.info(f"EEGSTREAM started.")

pid = os.getegid()
logging.info(f"Running with ID: {pid}")

ID_FILE = os.path.join(os.path.expanduser("~/"), ".eeg_process_id")
logging.info(f"ID file created in: {ID_FILE}")


if os.path.exists(ID_FILE):
    with open(ID_FILE, 'r') as file:
        oldpid = file.read()
        if oldpid.isdigit():
            oldpid = int(oldpid)
            if oldpid != pid:
                try:
                    os.kill(oldpid, signal.SIGKILL)
                except:
                    pass

with open(ID_FILE, 'w') as file:
    file.write(str(pid))


# ----------------------------------------------------------------------
@atexit.register
def goodbye():
    logging.info(f"Killing PID: {pid}")
    try:
        os.kill(pid, signal.SIGKILL)
        if os.path.exists(ID_FILE):
            os.remove(ID_FILE)
        # if os.path.exists('.running'):
            # os.remove('.running')
    except:
        pass


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

