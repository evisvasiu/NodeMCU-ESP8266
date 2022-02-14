
import machine
from machine import Pin
from time import sleep
import dht
from umqttsimple import MQTTClient
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
user = 'jezerca'
passw = 'Password@2'
client_id = 'esp8266'
topic_t = 'esp8266_temp'
topic_h = 'esp8266_humi'
def connect_and_subscribe():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server, user=user, password=passw)
  client.connect()
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
    sleep(10)
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
    deep_sleep(300000)
	
  except OSError as e:
    print('Failed to read sensor. Reconnecing...')
    restart_and_reconnect()

