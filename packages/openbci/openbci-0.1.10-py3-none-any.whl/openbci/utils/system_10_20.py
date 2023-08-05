# import netifaces
# import requests
# import nmap


# def wifi_modules():
    # ip_list = []

    # local_wlan0 = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
    # nm = nmap.PortScanner()
    # nm.scan(hosts=f'{local_wlan0}/24', arguments='-sn')
    # hosts = nm.all_hosts()

    # hosts = ['127.0.0.1', '192.168.1.113']

    # for host in hosts:
        # try:
            # response = requests.get(f'http://{host}/board', timeout=0.1)
            # if response.ok:
                # ip_list.append(host)
        # except:
            # continue

    # return ip_list


# print(ip4_addresses())

