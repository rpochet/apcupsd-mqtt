#!/usr/bin/python3
import json
import os
import time

import paho.mqtt.publish as publish
from apcaccess import status as apc


def main():
    mqtt_port = int(os.getenv('MQTT_PORT', 1883))
    mqtt_host = os.getenv('MQTT_HOST', 'localhost')
    interval = float(os.getenv('APCUPSD_INTERVAL', 10))
    alias = os.getenv('UPS_ALIAS', '')
    apcupsd_host = os.getenv('APCUPSD_HOST', '127.0.0.1')

    # Get initial data
    ups = apc.parse(apc.get(host=apcupsd_host))

    serial_no = ups.get('SERIALNO', '000000000000')
    model = ups.get('MODEL', 'Unknown')
    firmware = ups.get('FIRMWARE', 'FW 000.00')

    if not alias:
        alias = serial_no

    mqtt_topic = "apcupsd" + "/" + alias

    # Home Assistant
    print("Configuring Home Assistant...")

    discovery_msgs = []

    # Status
    status_topic = "homeassistant/sensor/apc_ups_" + alias + "/status/config"
    status_payload = {
        "device": {
            "identifiers": ["apc_ups_" + alias],
            "manufacturer": "APC",
            "name": alias,
            "model": model,
            "sw_version": firmware
        },
        "unique_id": "apc_ups_" + alias + "_status",
        "name": "apc_ups_" + alias + "_status",
        "state_topic": mqtt_topic,
        "value_template": "{{ value_json.status}}"
    }
    discovery_msgs.append({'topic': status_topic, 'payload': json.dumps(status_payload), 'retain': True})

    # Current input line voltage
    linev_topic = "homeassistant/sensor/apc_ups_" + alias + "/linev/config"
    linev_payload = {
        "device_class": "voltage",
        "device": {
            "identifiers": ["apc_ups_" + alias],
            "manufacturer": "APC", "name": alias,
            "model": model,
            "sw_version": firmware
        },
        "unique_id": "apc_ups_" + alias + "_linev",
        "name": "apc_ups_" + alias + "_line_voltage",
        "state_topic": mqtt_topic,
        "unit_of_measurement": "V",
        "value_template": "{{ value_json.linev}}"
    }
    discovery_msgs.append({'topic': linev_topic, 'payload': json.dumps(linev_payload), 'retain': True})

    # Percentage of UPS load capacity used
    loadpct_topic = "homeassistant/sensor/apc_ups_" + alias + "/loadpct/config"
    loadpct_payload = {
        "device_class": "power_factor",
        "device": {
            "identifiers": ["apc_ups_" + alias],
            "manufacturer": "APC",
            "name": alias,
            "model": model,
            "sw_version": firmware
        },
        "unique_id": "apc_ups_" + alias + "_loadpct",
        "name": "apc_ups_" + alias + "_load",
        "state_topic": mqtt_topic,
        "unit_of_measurement": "%",
        "value_template": "{{ value_json.loadpct}}"
    }
    discovery_msgs.append({'topic': loadpct_topic, 'payload': json.dumps(loadpct_payload), 'retain': True})

    # Current battery capacity charge percentage
    bcharge_topic = "homeassistant/sensor/apc_ups_" + alias + "/bcharge/config"
    bcharge_payload = {
        "device_class": "battery",
        "device": {
            "identifiers": ["apc_ups_" + alias],
            "manufacturer": "APC",
            "name": alias,
            "model": model,
            "sw_version": firmware
        },
        "unique_id": "apc_ups_" + alias + "_bcharge",
        "name": "apc_ups_" + alias + "_battery",
        "state_topic": mqtt_topic,
        "unit_of_measurement": "%",
        "value_template": "{{ value_json.bcharge}}"
    }
    discovery_msgs.append({'topic': bcharge_topic, 'payload': json.dumps(bcharge_payload), 'retain': True})

    # Remaining runtime left on battery as estimated by UPS
    timeleft_topic = "homeassistant/sensor/apc_ups_" + alias + "/timeleft/config"
    timeleft_payload = {
        "device": {
            "identifiers": ["apc_ups_" + alias],
            "manufacturer": "APC",
            "name": alias, "model": model,
            "sw_version": firmware
        },
        "unique_id": "apc_ups_" + alias + "_timeleft",
        "name": "apc_ups_" + alias + "_time_remaining",
        "state_topic": mqtt_topic,
        "unit_of_measurement": "S",
        "value_template": "{{ value_json.timeleft}}"
    }
    discovery_msgs.append({'topic': timeleft_topic, 'payload': json.dumps(timeleft_payload), 'retain': True})

    # Current battery voltage
    battv_topic = "homeassistant/sensor/apc_ups_" + alias + "/battv/config"
    battv_payload = {
        "device_class": "voltage",
        "device": {
            "identifiers": ["apc_ups_" + alias],
            "manufacturer": "APC",
            "name": alias,
            "model": model,
            "sw_version": firmware
        },
        "unique_id": "apc_ups_" + alias + "_battv",
        "name": "apc_ups_" + alias + "_battery_voltage",
        "state_topic": mqtt_topic,
        "unit_of_measurement": "V",
        "value_template": "{{ value_json.battv}}"
    }
    discovery_msgs.append({'topic': battv_topic, 'payload': json.dumps(battv_payload), 'retain': True})

    # Current power usage in watts
    power_topic = "homeassistant/sensor/apc_ups_" + alias + "/power/config"
    power_payload = {
        "device_class": "power",
        "device": {
            "identifiers": ["apc_ups_" + alias],
            "manufacturer": "APC",
            "name": alias,
            "model": model,
            "sw_version": firmware
        },
        "unique_id": "apc_ups_" + alias + "_power",
        "name": "apc_ups_" + alias + "_power",
        "state_topic": mqtt_topic,
        "unit_of_measurement": "W",
        "value_template": "{{ value_json.power}}"
    }
    discovery_msgs.append({'topic': power_topic, 'payload': json.dumps(power_payload), 'retain': True})

    publish.multiple(discovery_msgs, hostname=mqtt_host, port=mqtt_port, auth=None)

    while True:
        ups_data = apc.parse(apc.get(host=apcupsd_host), strip_units=True)

        status = {}

        # Calculate power
        try:
            max_watts = float(ups_data.get('NOMPOWER', 0.0))
            current_percent = float(ups_data.get('LOADPCT', 0.0))
            current_watts = ((max_watts * current_percent) / 100)
            ups_data['POWER'] = current_watts

        except:
            print("Failed to calculate power...")

        for k in ups_data:
            status[str(k).lower()] = str(ups_data[k])

        print(status)

        # Publish results
        publish.single(mqtt_topic, json.dumps(status), hostname=mqtt_host, port=mqtt_port, auth=None, retain=True)

        time.sleep(interval)


if __name__ == '__main__':
    main()
