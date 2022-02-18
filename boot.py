
import machine, onewire, ds18x20, time
from mqttsimple import MQTTClient
from time import sleep
from machine import Pin
import dht
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()
sleep_time = int(10000)

def deep_sleep(msecs):
  # configure RTC.ALARM0 to be able to wake the device
  rtc = machine.RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

  # set RTC.ALARM0 to fire after X milliseconds (waking the device)
  rtc.alarm(rtc.ALARM0, msecs)

  # put the device to sleep
  machine.deepsleep()

led = Pin(2, Pin.OUT)

ssid = 'Pixel5'
password = 'tir***021'

station = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

ap_if.active(False)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:  #The time it is still disconected to network
  for i in range(100):                 #Led pulsing while is disconected
    led.value(0)
    time.sleep(0.1)
    led.value(1)
    time.sleep(0.1)
    if station.isconnected() == True:   #if it connects to wifi, loop closes, and the execution can go on out of this while loop
      break
    if i == 60:                         #if it does not connect in 60 loop times, it will going to deep sleep.
      print('Could not connect to network. Going to sleep')
      deep_sleep(10000)                 #Going to deep sleep for 10 seconds.
    
print('Connection successful')
print(station.ifconfig())

"""
"umqttsimple" library is installed from here: 
https://raw.githubusercontent.com/RuiSantosdotme/ESP-MicroPython/master/code/MQTT/umqttsimple.py
"""
ds_pin = machine.Pin(14)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()
print('Found DS devices: ', roms)

mqtt_server = '13*46.220'
user = 'je***ca'
passw = '*'
client_id = 'esp8266'
topic_t = 'esp8266_temp'
topic_h = 'esp8266_humi'
topic_sub = 'sleep'
topic_ds = 'ds18'

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
    led.value(1)
    ds_sensor.convert_temp()
    sleep(10)
    for rom in roms:
      print(rom)
      print(ds_sensor.read_temp(rom))
    msg_ds = b'%3.0f' %ds_sensor.read_temp(rom)
    client.publish(topic_ds, msg_ds)
    led.value(0)
    sleep(1)
    print('Going to deep sleep')
    #deep sleep command
    print(sleep_time)
    deep_sleep(sleep_time)
    
  except OSError as e:
    print('Failed to read sensor. Reconnecing...')
    restart_and_reconnect()

