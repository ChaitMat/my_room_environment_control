# Web app to control the AC over the internet.
This project is a web app to control an AC (Air Conditioner) in my room. Raspberry pi is used to host the web app and control the AC using an IR blaster.
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

## Decoding IR (Infra Red) codes

The IR codes to control the AC are decoded using the [LIRC](http://www.lirc.org/). Refer this [blog](http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/) to decode a the IR signal for a particular remote and setup the Raspberry PI for IR signal transmission through the IR blaster circuit.

The decoded IR codes are stored in a file called lirc. Following are the sample codes:-

```
 # contributed by : Chaitanya M
 #
 # brand:                       LG
 # model no. of remote control: 6711A20109B
 # devices being controlled by this remote:AIR CONDITIONER


begin remote

  name  LG
  bits           28
  flags CONST_LENGTH
  eps            30
  aeps          100

  header       8400  4200
  one           651  1515
  zero          651   459
  ptrail        651
  gap          103993



      begin codes

        AC16_LOW_TURNON		0x8800101
        AC16_MED_TURNON		0x8800123
        AC16_HI_TURNON		0x8800145
        
      end codes

end remote
```

