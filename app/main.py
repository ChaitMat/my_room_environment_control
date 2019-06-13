#!/usr/bin/env python3

#__________Library Imports__________#

from flask import Flask, request, render_template

from celery import Celery
from celery.schedules import crontab
from celery.task.control import revoke

import datetime
import time

#__________Package Imports__________#
from get_records import getrecords
from remote_records.publish_state import  publish_remote_state
from remote_records.log_state import  log_remote_state
from remote_records.get_last_records import get_last_records
from send_signal import send_signal
from publish_set_sleep import publish_set_sleep




#Create Flask instance
app = Flask(__name__)  
app.debug = True


#Create Celery instance with connection to the local Redis broker
celery = Celery(app.name, broker= 'redis://localhost:6379/0')  


#Configuration to schedule the execution of task "update_temperature_task" after every 10mins
app.config['CELERYBEAT_SCHEDULE']  = {
    'update_temp-celery': {
        'task': 'celery_tasks.update_temperature.update_temperature_task',
        'schedule': crontab(minute="*/10"),     
    }
}
app.config['CELERY_IMPORTS'] = ('celery_tasks.update_temperature')
celery.conf.update(app.config)


# Function returns the "index.html" page when called by client
@app.route('/')
def index():

    return render_template("index.html")
    
   
# Function returns the temperature history to update the chart when called by client
@app.route("/update_chart", methods=['POST'])
def update_chart():

    hrs = request.form['hours']
    hours = "-"+str(hrs)+" hours"
    temp = getrecords(hours)

    return temp 
    

# Function returns the "remote.html" page when called by client
@app.route('/remote_control')
def remote_control():

    return render_template("remote.html")
    

# Function is used to turn the AC ON/OFF when the power button is pressed 
# and publish the changed state of the AC to the clients.
@app.route('/power_control', methods=['POST'])
def power_control():

    # Parse the data recieved via the POST request
    state = request.form['STATE']              #state -> Current state of AC (ON/OFF)
    temp = request.form['TEMP']		       #temp -> Current temperature of AC
    fan_speed = request.form['FAN_SPEED']      #fan_speed -> Current fanspeed of AC
    
    
    """
    Variable descriptions
    key -> The key required to send IR signal via LIRC. Format AC<temperature>_<fan speed>_<action>, Eg. AC24_LOW_TURNON 
    send_state -> Send the updated state to update the clients
    state_log -> Stores the updated state to log in the database
    """
    
    if state == "OFF":
        key = "AC" + str(temp) + "_" + str(fan_speed) + "_" + "TURNON"
	    send_state = "ON"
	    state_log = "TURNON"
	
    elif state == "ON":
        key = "AC_TURNOFF"
	    send_state = "OFF"
	    state_log = "TURNOFF_MANUAL"
	
	
    #Send the IR signal	
    send_signal(key)

    current_data = {
                    "TEMP" : temp,
                    "STATE" : send_state,
                    "FAN_SPEED" : fan_speed
                   }

    log_remote_state(state_log, int(temp), fan_speed) #Calls the function to log the updated state

    publish_remote_state(current_data) #Calls the function to publish the updated state

    return '{}'
    

# Function is used to increase the teperature of the AC 
# and publish the changed state of the AC to the clients.
@app.route("/temp_up_control", methods=['POST'])
def temp_up_control():

    state = request.form['STATE']
    temp = request.form['TEMP']
    fan_speed = request.form['FAN_SPEED']

    if int(temp) < 30: #Max output air temperature of AC is 30degC
        update_temp = int(temp) + 1
    else:
        update_temp = int(temp)

    if state == "ON": # IR signal will only be sent if the AC is in the ON state
        key = "AC" + str(update_temp) + "_" + str(fan_speed) + "_" + "ON"
        send_signal(key)      

    current_data = {
                    "TEMP" : str(update_temp),
                    "STATE" : state,
                    "FAN_SPEED" : fan_speed
                   }

    if state == "ON": # Action will only be logged if the AC is in the ON state
        log_remote_state(state, update_temp, fan_speed)

    publish_remote_state(current_data)

    return '{}'

# Function is used to decrease the teperature of the AC 
# and publish the changed state of the AC to the clients.
@app.route("/temp_down_control", methods=['POST'])
def temp_down_control():

    state = request.form['STATE']
    temp = request.form['TEMP']
    fan_speed = request.form['FAN_SPEED']

    if int(temp) > 16: #Min output air temperature of AC is 16degC
        update_temp = int(temp) - 1
    else:
        update_temp = int(temp)

    if state == "ON":
        key = "AC" + str(update_temp) + "_" + str(fan_speed) + "_" + "ON"
        send_signal(key)      

    current_data = {
                    "TEMP" : str(update_temp),
                    "STATE" : state,
                    "FAN_SPEED" : fan_speed
                 }

    if state == "ON":
        log_remote_state(state, update_temp, fan_speed)

    publish_remote_state(current_data)

    return '{}'

# Function is used to increase the fan speed of the AC 
# and publish the changed state of the AC to the clients.
@app.route("/fan_up_control", methods=['POST'])
def fan_up_control():

    state = request.form['STATE']
    temp = request.form['TEMP']
    fan_speed = request.form['FAN_SPEED']
    
    #Fan speed can be LOW -> MED -> HI
    if fan_speed == "LOW":
        update_fan_speed = "MED"
    elif fan_speed == "MED":
        update_fan_speed = "HI"
    elif fan_speed == "HI":
        update_fan_speed = "HI"

    if state == "ON":
        key = "AC" + str(temp) + "_" + str(update_fan_speed) + "_" + "ON"
        send_signal(key)      

    current_data = {
                    "TEMP" : str(temp),
                    "STATE" : state,
                    "FAN_SPEED" : update_fan_speed
                 }

    if state == "ON":
        log_remote_state(state, int(temp), update_fan_speed)

    publish_remote_state(current_data)

    return '{}'
    

# Function is used to decrease the fan speed of the AC 
# and publish the changed state of the AC to the clients.
@app.route("/fan_down_control", methods=['POST'])
def fan_down_control():

    state = request.form['STATE']
    temp = request.form['TEMP']
    fan_speed = request.form['FAN_SPEED']

    if fan_speed == "HI":
        update_fan_speed = "MED"
    elif fan_speed == "MED":
        update_fan_speed = "LOW"
    elif fan_speed == "LOW":
        update_fan_speed = "LOW"

    if state == "ON":
        key = "AC" + str(temp) + "_" + str(update_fan_speed) + "_" + "ON"
        send_signal(key)      

    current_data = {
                    "TEMP" : str(temp),
                    "STATE" : state,
                    "FAN_SPEED" : update_fan_speed
                   }

    if state == "ON":
        log_remote_state(state, int(temp), update_fan_speed)

    publish_remote_state(current_data)

    return '{}'
    

#Function is used set the sleep mode
@app.route("/set_sleep", methods=['POST'])
def set_sleep():
    set_time = request.form['set_time']

    publish_set_sleep(set_time)

    global result #Variable is made Global so that it can be accessed by cancel_sleep function

    result = set_ac_sleep.delay(set_time) #Create the set_ac_sleep() celery function

    return '{}'
    

#Function is used cancel the sleep mode.
@app.route("/cancel_sleep")
def cancel_sleep():

    result.revoke(terminate = True)  
 
    publish_set_sleep('cancel')

    return '{}'
    

# Celery task to run the sleep mode asynchronously
@celery.task
def set_ac_sleep(time_to_sleep):

    # Find the time difference in seconds between the current time and the time set to sleep 
    time_now = time.strftime("%H:%M")

    FMT = '%H:%M'
    tdelta = datetime.datetime.strptime(time_to_sleep, FMT) - datetime.datetime.strptime(time_now, FMT)

    if tdelta.days < 0:
        tdelta = datetime.timedelta(days = 0, seconds=tdelta.seconds)

    delay_time = tdelta.total_seconds()

    time.sleep(delay_time) #Delay the function upto the time at which the AC will turn off.

    send_signal('AC_TURNOFF')

    current_state = get_last_records()

    current_data = {
                    "TEMP" : str(current_state[0][2]),
                    "STATE" : 'OFF',
                    "FAN_SPEED" : current_state[0][3]
                    }

    log_remote_state('TURNOFF_AUTO', int(current_data["TEMP"]), current_data["FAN_SPEED"])

    publish_remote_state(current_data)

    publish_set_sleep('cancel')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080) 
