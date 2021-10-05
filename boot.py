import uos, machine
import gc
import webrepl
import network
import config

webrepl.start()
gc.collect()

SSID = config.SSID
PASS_WIFI = config.PASS_WIFI

def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, PASS_WIFI)
        while not sta_if.isconnected():
            pass
    ip_conf = sta_if.ifconfig()
    print("ip:\t"+ ip_conf[0] + "\n" + "mask:\t"+ip_conf[1] +"\n"+ "gw:\t"+ip_conf[2])

connect()
