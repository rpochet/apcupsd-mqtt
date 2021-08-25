#!/usr/bin/python
import os
import time
from prettytable import PrettyTable
import paho.mqtt.client as paho
from apcaccess import status as apc
import socket

MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
INTERVAL = float(os.getenv('INTERVAL', 15))
UPS_ALIAS = os.getenv('UPS_ALIAS',socket.gethostname())
APCUPSD_HOST = os.getenv('APCUPSD_HOST','127.0.0.1')

t = PrettyTable(['Key','Value'])
t.add_row(['MQTT_USER', MQTT_USER])
t.add_row(['MQTT_PASSWORD', MQTT_PASSWORD])
t.add_row(['MQTT_HOST', MQTT_HOST])
t.add_row(['INTERVAL', INTERVAL])
t.add_row(['UPS_ALIAS', UPS_ALIAS])
t.add_row(['ACPUPSD_HOST', APCUPSD_HOST])

def pub_mqtt( topic, value):
    """
    Publishes a new value to a mqtt topic.
    :param topic: 
    :param value: 
    :return: nothing
    """
    value =  str(value)
    client1 = paho.Client("control1")  # create client object
    #if MQTT_USER is not None and MQTT_PASSWORD is not None:
    client1.username_pw_set(MQTT_USER,MQTT_PASSWORD)
    try:
        client1.connect(MQTT_HOST, MQTT_PORT)  # establish connection
    except:
        print("Unable to connect to MQTT broker at %s:%i" % (MQTT_HOST, MQTT_PORT))

    return client1.publish(topic, value)

def main():
    MQTT_TOPIC_PREFIX="/apcupsd"
    ups = apc.parse(apc.get(host=APCUPSD_HOST))
    HOSTNAME = ups.get('HOSTNAME', 'apcupsd-mqtt')
    MQTT_TOPIC_PREFIX = MQTT_TOPIC_PREFIX + "/" + UPS_ALIAS + "/"

    first_run = True

    while True:
        ups_data = apc.parse(apc.get(host=APCUPSD_HOST), strip_units=True)

        try:
            max_watts = float(ups_data.get('NOMPOWER', 0.0))
            current_percent = float(ups_data.get('LOADPCT', 0.0))
            current_watts = ((max_watts*current_percent)/100)
            ups_data['WATTS'] = current_watts

        except:
            print("Failed to calculate watts...")

        for k in ups_data:
            topic_id = MQTT_TOPIC_PREFIX + str(k)
            if first_run:
                print("%s = %s" % (topic_id, str(ups_data[k])))
            pub_mqtt( topic_id, str(ups_data[k]) )
        if first_run:
            first_run = False
        time.sleep(INTERVAL)


if __name__ == '__main__':
    main()
