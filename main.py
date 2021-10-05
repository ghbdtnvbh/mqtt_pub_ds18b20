from umqtt.simple import MQTTClient
import machine
import onewire, ds18x20
import time
#import json
import config

DEEP_SLEEP_TIME = 15
PIN = machine.Pin(2)  # WemosD1 pin2(D4), NodeMCU pin4(D2)
CLIENT_ID = "esp8266sn558j"
MQTT_SERVER = "broker.hivemq.com"
TOPIC_PUB = 'sensors1255'

ds = ds18x20.DS18X20(onewire.OneWire(PIN))
time.sleep(5)

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_SERVER)
    client.connect()
    print('Connected to %s MQTT broker' % (MQTT_SERVER))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker!  Reconnecting...')
    time.sleep(10)
    machine.reset()
# при вызове deepsleep контроллер уснёт на значение переменной DEEPSLEEP минут 
# и загрузится заново, аналогично нажатию reset
# небходимо припаять wake на reset, на плате LoLin: D0 и RST

def deep_sleep():
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, DEEP_SLEEP_TIME*60*1000) 
    machine.deepsleep()
    
# для для более точного измерения темпиратуры, 
# считываем 5 раз и возвращаем среднее значение 
def read_18b20_sensor():
    try:
        array_measure = []
        roms = ds.scan()
        for i in range(5):
            ds.convert_temp()
            time.sleep_ms(1500)
    except onewire.OneWireError as err: #Если считать датчик не удалось, рестарт МК
        print(" Failed to read sensor!")
        restart_and_reconnect()
    else:
        for rom in roms:
            temp = ds.read_temp(rom)
            array_measure.append(temp)
    return sum(array_measure) / len(array_measure)
    

try:
  client = connect_mqtt()
except OSError as e:
    restart_and_reconnect()

while True:
    try:
        mean_value = read_18b20_sensor()
        resul = 'temp value2='+str(round(mean_value, 1))
        #rounding_value = round(mean_value, 1)
        #rv_to_json = {"value":rounding_value} - публиковать в формате JSON
        #resul = json.dumps(rv_to_json)
        #print(resul)
        client.publish(TOPIC_PUB, resul)
        time.sleep_ms(1000)
        print("temp =  %s Send to MQTT broker" % (mean_value))
        client.disconnect()
        print("DEEPSLEEP MODE - %s min" % (DEEP_SLEEP_TIME))
        deep_sleep()
    except OSError as e:
        restart_and_reconnect()
