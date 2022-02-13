from machine import Pin
from time import sleep
import dht
from umqttsimple import MQTTClient
"""
"umqttsimple" library is installed from here: 
https://raw.githubusercontent.com/RuiSantosdotme/ESP-MicroPython/master/code/MQTT/umqttsimple.py
"""

sensor = dht.DHT22(Pin(14))

mqtt_server = '138.3.246.***'
user = 'j*****a'
passw = '*******'
client_id = 'esp8266'
topic_t = 'esp8266_temp'
topic_h = 'esp8266_temp'
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
    client.check_msg()
    sleep(5)
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    print('Temperature: %3.1f C' %temp)
    print('Humidity: %3.1f %%' %hum)
    msg_t = b'%3.1f' %temp
    msg_h = b'%3.1f' %hum
    client.publish(topic_t, msg_t)
    client.publish(topic_h, msg_h)
	
  except OSError as e:
    print('Failed to read sensor. Reconnecing...')
    restart_and_reconnect()
