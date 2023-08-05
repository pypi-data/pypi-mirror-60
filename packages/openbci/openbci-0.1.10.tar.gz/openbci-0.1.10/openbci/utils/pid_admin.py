import os
import logging
import atexit
import signal
from pathlib import Path


# ----------------------------------------------------------------------
def autokill_process():
    """"""
    pid = os.getpid()
    logging.info(f"Running with PID: {pid}")

    ID_FILE = os.path.join(Path.home(), ".openbci.pid")
    logging.info(f"PID file created in: {ID_FILE}")

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
    def _():
        logging.info(f"Killing PID: {pid}")
        try:
            os.kill(-pid, signal.SIGKILL)
            if os.path.exists(ID_FILE):
                os.remove(ID_FILE)
        except:
            pass

