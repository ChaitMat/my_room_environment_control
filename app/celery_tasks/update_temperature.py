#Celery task that retreives temperature and humidity sensor from DHT22 sensor 
#Publish the temperature data via MQTT
#Log the temperature in the database

import celery
import paho.mqtt.publish as publish
import Adafruit_DHT
import sqlite3

data_base_path = '/var/www/lab_app/lab_app.db'

def log_values(sensor_id, temp, hum):
	conn=sqlite3.connect(data_base_path)
	curs=conn.cursor()
	curs.execute("""INSERT INTO temperatures values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", (sensor_id,temp))
	curs.execute("""INSERT INTO humidities values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", (sensor_id,hum))
	conn.commit()
	conn.close()

def get_last_record():
    last_record = []
    conn=sqlite3.connect(data_base_path)
    curs=conn.cursor()
    curs.execute('select * from temperatures order by rDatetime desc limit 1;')
    last_record.append(curs.fetchall())
    curs.execute('select * from humidities order by rDatetime desc limit 1;')
    last_record.append(curs.fetchall())
    conn.close()
    return last_record

@celery.task
def update_temperature_task():
    humidity, temperature  = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)

    if humidity is not None and temperature is not None: 
        publish.single("temperature/sensor01",str(round(temperature,2))+"\xb0"+"C", qos = 0 , retain = True, hostname="localhost", port=1883, client_id="CMM", keepalive=60)
        log_values("1", temperature, humidity)

    else:
        records = get_last_record() #If the temperature and humidity values cannot be retreived from the sensors the last record in the database is retreived and published
        temperature = records[0]
        humidity = records[1]
        publish.single("temperature/sensor01",str(round(temperature,2))+"\xb0"+"C", qos = 0 , retain = True, hostname="localhost", port=1883, client_id="CMM", keepalive=60)
        log_values("1", temperature, humidity)




 
