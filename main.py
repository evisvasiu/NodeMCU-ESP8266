

import time
from mqttsimple import MQTTClient
from time import sleep
import machine
from machine import Pin
import dht


"""
"umqttsimple" library is installed from here: 
https://raw.githubusercontent.com/RuiSantosdotme/ESP-MicroPython/master/code/MQTT/umqttsimple.py
"""
led = Pin(2, Pin.OUT)
sensor = dht.DHT22(Pin(14))

def deep_sleep(msecs):
  # configure RTC.ALARM0 to be able to wake the device
  rtc = machine.RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

  # set RTC.ALARM0 to fire after X milliseconds (waking the device)
  rtc.alarm(rtc.ALARM0, msecs)

  # put the device to sleep
  machine.deepsleep()

mqtt_server = '138.3.246.220'
user = 'je*****'
passw = '*****'
client_id = 'esp8266'
topic_t = 'esp8266_temp'
topic_h = 'esp8266_humi'
topic_sub = 'sleep'
sleep_time = int(10000)

def sub_cb(topic, msg):
  global sleep_time
  sleep_time = int(msg)
  if topic == b'notification' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, user=user, password=passw)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(20)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    sleep(20)
    client.check_msg()
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    print('Temperature: %3.1f C' %temp)
    print('Humidity: %3.1f %%' %hum)
    msg_t = b'%3.1f' %temp
    msg_h = b'%3.1f' %hum
    client.publish(topic_t, msg_t)
    client.publish(topic_h, msg_h)
    led.value(1)
    sleep(5)
    print('Going to deep sleep')
    #deep sleep command
    print(sleep_time)
    deep_sleep(sleep_time)
	
  except OSError as e:
    print('Failed to read sensor. Reconnecing...')
    restart_and_reconnect()

