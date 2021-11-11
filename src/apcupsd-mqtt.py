#!/usr/bin/python3
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

import paho.mqtt.publish as publish
from apcaccess import status as apc
from yaml import safe_load

BASE_DIR = Path(__file__).parent

SensorConfig = NamedTuple('SensorConfig', [('topic', str), ('payload', Dict['str', Any])])


def main():
    debug_logging = os.getenv('DEBUG', '0') == '1'
    mqtt_port = int(os.getenv('MQTT_PORT', 1883))
    mqtt_host = os.getenv('MQTT_HOST', 'localhost')
    mqtt_user = os.getenv('MQTT_USER')
    mqtt_password = os.getenv('MQTT_PASSWORD')

    mqtt_auth = {'username': mqtt_user, 'password': mqtt_password} if mqtt_user and mqtt_password else None

    interval = float(os.getenv('APCUPSD_INTERVAL', 10))
    alias = os.getenv('UPS_ALIAS', '')
    apcupsd_host = os.getenv('APCUPSD_HOST', '127.0.0.1')

    print('Get initial data from UPS... {!r}'.format(apcupsd_host), file=sys.stderr)
    ups = apc.parse(apc.get(host=apcupsd_host))

    serial_no = ups.get('SERIALNO', '000000000000')
    model = ups.get('MODEL', 'Unknown')
    firmware = ups.get('FIRMWARE', 'FW 000.00')

    if not alias:
        alias = serial_no

    mqtt_topic = 'apcupsd/{}'.format(alias)
    config = Config(serial_no, alias, model, firmware, mqtt_topic)

    print('Configuring Home Assistant via MQTT Discovery...', file=sys.stderr)
    discovery_msgs = [
        {
            'topic': sensor.topic,
            'payload': json.dumps(sensor.payload, sort_keys=True),
            'retain': True,
        }
        for sensor in config.sensors
    ]

    publish.multiple(discovery_msgs, hostname=mqtt_host, port=mqtt_port, auth=mqtt_auth)

    print('Starting value updater loop...', file=sys.stderr)

    while True:
        ups_data = apc.parse(apc.get(host=apcupsd_host), strip_units=True)

        # Calculate power
        try:
            max_watts = float(ups_data.get('NOMPOWER', 0.0))
            current_percent = float(ups_data.get('LOADPCT', 0.0))
            ups_data['POWER'] = ((max_watts * current_percent) / 100)
        except:
            print('Failed to calculate power...', file=sys.stderr)

        status = {
            key.lower(): str(value)
            for key, value in ups_data.items()
        }
        status_string = json.dumps(status, sort_keys=True)

        if debug_logging:
            print(status_string)

        # Publish results
        publish.single(mqtt_topic, status_string, hostname=mqtt_host, port=mqtt_port, auth=mqtt_auth, retain=True)

        time.sleep(interval)


class Config:
    SENSOR_TYPES = (
        'binary_sensor',
        'sensor',
    )

    def __init__(self, serial_no, alias, model, firmware, mqtt_topic):
        self.__serial_no = serial_no
        self.__alias = alias
        self.__model = model
        self.__firmware = firmware
        self.__mqtt_topic = mqtt_topic

        with BASE_DIR.joinpath('config.yml').open() as fd:
            raw_config = safe_load(fd)

        self.__sensors = []
        for sensor_type in self.__class__.SENSOR_TYPES:
            raw_sensors = raw_config.get(sensor_type) or {}

            self.__sensors.extend([
                self.__get_device_descriptor(sensor_type, name, config)
                for name, config in sorted(raw_sensors.items())
            ])

    def __get_device_descriptor(self, sensor_type: str, name: str, config: Optional[dict]) -> SensorConfig:
        if config is None:
            config = {}

        query_key = name
        if '_key' in config:
            query_key = config.pop('_key')

        topic = 'homeassistant/{}/apc_ups_{}/{}/config'.format(sensor_type, self.__alias, query_key)

        payload = {
            'device': {
                'identifiers': [
                    'apc_ups_{}'.format(self.__serial_no),
                ],
                'manufacturer': 'APC',
                'name': self.__alias,
                'model': self.__model,
                'sw_version': self.__firmware,
            },
            'unique_id': 'apc_ups_{}_{}'.format(self.__serial_no, query_key),
            'name': 'apc_ups_{}_{}'.format(self.__alias, name),
            'state_topic': self.__mqtt_topic,
            'value_template': '{{{{value_json.{}}}}}'.format(query_key),
        }
        payload.update(config)

        return SensorConfig(topic, payload)

    @property
    def sensors(self) -> List[SensorConfig]:
        return self.__sensors


if __name__ == '__main__':
    main()
