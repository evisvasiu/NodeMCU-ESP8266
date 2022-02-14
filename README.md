# NodeMCU-ESP8266
NodeMCU-v3 ESP8266

Reading and publishing multiple weather sensors data.

umqttsimple.py - This file is the MQTT library.

main.py - This file because of its name, runs automatically after boot.py and contains the script which reads data from multiple sensors and publishes them to MQTT broker.

boot.py - This is the first file which runs first on power up/reset and contains the code for wifi connection.
