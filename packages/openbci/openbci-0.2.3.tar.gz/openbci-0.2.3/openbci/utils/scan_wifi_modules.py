import netifaces
import requests
import nmap


# ----------------------------------------------------------------------
def scan():
    """"""
    ip_list = {}
    try:
        local_wlan0 = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
    except:
        local_wlan0 = netifaces.ifaddresses('wlp2s0')[netifaces.AF_INET][0]['addr']

    nm = nmap.PortScanner()
    nm.scan(hosts=f'{local_wlan0}/24', arguments='-sn')
    hosts = nm.all_hosts()

    for host in hosts:
        try:
            response = requests.get(f'http://{host}/board', timeout=0.1)
            if response.ok:
                ip_list[host] = response.json
        except:
            continue

    return ip_list


if __name__ == '__main__':
    scan()
