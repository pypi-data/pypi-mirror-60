# OpenBCI
Hight level Python module for OpenBCI hardware.

::: warning
  * This is NOT an official package from [OpenBCI team](https://openbci.com/).
  * This module is still unstable and not recommended for use in production.
:::

## What is?

A Python module for interaction with [OpenBCI boards](https://openbci.com/).
Currently, we have support for Cyton (and Daisy) and their WiFi module.
All source code can be accessed from our [bitbucket repository](https://bitbucket.org/gcpds/python-openbci/src/master/).

## What do we want?

We want a stable, high level, easy to use and extensible Python module for work
with OpenBCI, for students and researchers. We are developing a set of tools for
preprocessing, real-time data handling and streaming.

## Who are we?
We are a research group focused on digital processing of signals and machine
learning from the National University of Colombia at Manizales ([GCPDS](http://www.hermes.unal.edu.co/pages/Consultas/Grupo.xhtml;jsessionid=8701CFAD84FB5D540090846EA8912D48.tomcat6?idGrupo=615&opcion=1>)).

## How works?

An acquisition object can be instantiated from differents backend imlplementation:
Serial, WiFi and WebSockets.

### Synchronous
For more details refers to [Cyton data acquisition](_notebooks/data_acquisition.html#Cyton).


```python
from openbci.acquisition import CytonRFDuino as Device
# from openbci.acquisition import CytonWiFi as Device

openbci = Device()
openbci.collect(5)

eeg_data = openbcib.eeg_buffer()
```

### Aynchronous
For more details refers to [WiFi data acquistion](_notebooks/data_acquisition.html#WiFi).


```python
from openbci.acquisition import CytonRFDuino as Device
# from openbci.acquisition import CytonWiFi as Device

openbci = Device()
openbci.start_collect()
# some python stuff 
openbci.stop_collect()

eeg_data = openbcib.eeg_buffer()
```

### WebSockets
For more details refers to [WebSockets data acquistion](_notebooks/data_stream.html#access-to-stream-from-python).


```python
from openbci.stream.ws import CytonWS_decorator

@CytonWS_decorator()
def eeg_with_ap(ws, eeg_data):
    """"""
    # some python stuff 
```

### API

## Contact:

Main developer: Yeison Cardona yencardonaal@unal.edu.co, [\@yeisondev](https://twitter.com/yeisondev).
