#Module to publish the sleep time to multiple clients via MQTT

import paho.mqtt.publish as publish

def publish_set_sleep(set_time_to_sleep):

    publish.single("remote/update04",set_time_to_sleep, qos = 0 ,retain = True, hostname="localhost", port=1883, client_id="CMM", keepalive=60)


