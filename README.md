# Web app to control the AC over the internet.
This project is a web app to control an AC in my room. Raspberry pi is used to host the web app and control the AC using an IR blaster.
Thw web app is built using a Flask framework and MQTT protocol is used to publish data to multiple users. Celery is used to scedule tasks and run asynchronous tasks.

## Features of the app

* View current temperature of the room
* View temperature history of the room.
* Automatically acquire temperature data from the temperature sensor after every 10 mins.
* Control the AC by switching it ON/OFF, controlling the air temperature and fan speed.
* Sleep mode

## Hardware requirements

* Raspberry Pi connected to the internet.
* DHT22/11 temeprature and humidity sensor.
* [IR blaster circuit](https://cdn.instructables.com/F1I/Y78D/JE94HH0B/F1IY78DJE94HH0B.LARGE.jpg) 
