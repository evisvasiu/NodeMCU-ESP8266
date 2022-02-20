

import machine, onewire, ds18x20, time
from mqttsimple import MQTTClient
from time import sleep
from machine import Pin, ADC
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

ssid = 'K*x-1B6C'
password = '80*562743'

station = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

ap_if.active(False)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:         #The time it is still disconected to network
  for i in range(100):                       #Led pulsing while is disconected
    led.value(0)
    time.sleep(0.1)
    led.value(1)
    time.sleep(0.1)
    if station.isconnected() == True:         #if it connects to wifi, loop closes, and the execution can go on out of this while loop
      break
    if i == 60:                               #if it does not connect in 60 loop times, it will going to deep sleep.
      print('Could not connect to network. Going to sleep')
      #deep_sleep(sleep_time)                 #Going to deep sleep for a specified amount of time
    
print('Connection successful')

print(station.ifconfig())

"""
"umqttsimple" library is installed from here: 
https://raw.githubusercontent.com/RuiSantosdotme/ESP-MicroPython/master/code/MQTT/umqttsimple.py
"""
uv = ADC(0)                 #UV sensor connected to analog pin 0
dht22 = dht.DHT22(Pin(14))  #DHT22 connected to pin GPIO14
ds_pin = machine.Pin(5)     #DS18 connected to pin GPIO5
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()
print('Found DS devices: ', roms)

mqtt_server = '138*.220'
user = 'j*'
passw = 'P*d@2'
client_id = 'esp8266'
topic_uv = 'uv'
topic_t = 'dht22_temp'
topic_h = 'dht22_humi'
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
  sleep(10)
  machine.reset()
try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    led.value(1)
    uv_volt = (uv.read()*3300)/1023
    dht22.measure()             #dht22 read function
    temp = dht22.temperature()  #reading dht22 temp
    humi = dht22.humidity()     #reading dht22 humidity
    ds_sensor.convert_temp()    #reading ds18 temp
    sleep(10)
    print('UV Index mV: %3.0f' %uv_volt)
    print('Temperature: %3.1f C' %temp)
    print('Humidity: %3.1f %%' %humi)
    msg_uv = b'%3.0f' %uv_volt
    msg_temp = b'%3.1f' %temp   #saving dht22 value
    msg_humi = b'%3.1f' %humi   #saving dht22 value
    for rom in roms:
      #print(rom)
      print('DS18 Temperature: %3.1f C' %ds_sensor.read_temp(rom))
    msg_ds = b'%3.1f' %ds_sensor.read_temp(rom) #saving ds18 value
    client.publish(topic_uv, msg_uv)          #publish uv index
    client.publish(topic_t, msg_temp)           #publish dht temp
    client.publish(topic_h, msg_humi)           #publish dht humidity
    client.publish(topic_ds, msg_ds)            #publish ds18 temp
    led.value(0)
    sleep(2)
    #print('Going to deep sleep')                #deep sleep command
    #print(sleep_time)
    #deep_sleep(sleep_time)
    
  except OSError as e:
    print('Failed to read sensor. Reconnecing...')
    restart_and_reconnect()



