#Module to publish the updated state via MQTT 

import paho.mqtt.publish as publish
import json

def publish_remote_state(current_data):


    publish.single("remote/update01",json.dumps(current_data), qos = 0 , retain = True, hostname="localhost", port=1883, client_id="CMM", keepalive=60)
    
