# NodeMCU-ESP8266
NodeMCU-v3 ESP8266

umqttsimple.py - this file is the MQTT library.

main.py - this file because of its name, runs automatically after boot.py and contains the script which reads dht22 data and publishes them to MQTT broker.

boot.py - This file runs first on power up/reset and contains the code for wifi connection.
