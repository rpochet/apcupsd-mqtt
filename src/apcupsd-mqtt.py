#!/usr/bin/python3
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

import paho.mqtt.publish as publish
from apcaccess import status as apc
<<<<<<< HEAD
import logging
import socket
import pyfiglet

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'gladys/master/device')
INTERVAL = float(os.getenv('INTERVAL', 15))
UPS_ALIAS = os.getenv('UPS_ALIAS', socket.gethostname())
APCUPSD_HOST = os.getenv('APCUPSD_HOST', '127.0.0.1')
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)
logger.setLevel(LOG_LEVEL)

t = PrettyTable(['Key','Value'])
t.add_row(['MQTT_USER', MQTT_USER])
t.add_row(['MQTT_PASSWORD', MQTT_PASSWORD])
t.add_row(['MQTT_HOST', MQTT_HOST])
t.add_row(['MQTT_TOPIC', MQTT_TOPIC])
t.add_row(['INTERVAL', INTERVAL])
t.add_row(['UPS_ALIAS', UPS_ALIAS])
t.add_row(['ACPUPSD_HOST', APCUPSD_HOST])
t.add_row(['LOG_LEVEL', LOG_LEVEL])

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
        logger.error("unable to connect to mqtt on %s:%i" % (MQTT_HOST, MQTT_PORT))
=======
from yaml import safe_load

SensorConfig = NamedTuple('SensorConfig', [('topic', str), ('payload', Dict['str', Any])])

__FILE = Path(__file__)
_LOGGER = logging.getLogger(__FILE.name)
BASE_DIR = __FILE.parent

MQTT_CLIENT_ID = __FILE.name
MQTT_TOPIC = 'apcupsd'

exiting_main_loop = False


class Config:
    SENSOR_TYPES = (
        'binary_sensor',
        'sensor',
    )

    def __init__(self, serial_no, alias, model, firmware, mqtt_state_topic: str, mqtt_availability_topic: str):
        self.__serial_no = serial_no
        self.__alias = alias
        self.__model = model
        self.__firmware = firmware
        self.__mqtt_state_topic = mqtt_state_topic
        self.__availability_topic = mqtt_availability_topic

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
            'availability_topic': self.__availability_topic,
            'state_topic': self.__mqtt_state_topic,
            'json_attributes_topic': self.__mqtt_state_topic,
            'value_template': '{{{{value_json.{}}}}}'.format(query_key),
        }
        payload.update(config)
>>>>>>> c4b141a79bd293e1ec23ceae1025acfcc5d5ba71

        return SensorConfig(topic, payload)

    @property
    def sensors(self) -> List[SensorConfig]:
        return self.__sensors


class MqttClient:
    def __init__(self, broker_host: str, broker_port: int, broker_auth: Optional[dict] = None):
        self.__connection_options = {
            'hostname': broker_host,
            'port': broker_port,
            'auth': broker_auth,
            'client_id': MQTT_CLIENT_ID
        }

    def publish_multiple(self, payloads: List[Dict[str, Any]], **kwargs) -> None:
        publish.multiple(payloads, **self.__connection_options, **kwargs)

    def publish_single(self, topic: str, payload: str, **kwargs) -> None:
        publish.single(topic, payload, **self.__connection_options, **kwargs)


class HaCapableMqttClient(MqttClient):
    def __init__(self, base_topic: str, **kwargs):
        self.__base_topic = base_topic
        self.__status_topic = self.get_abs_topic('status')

        self.__published_status = None

        super().__init__(**kwargs)

    @property
    def status_topic(self) -> str:
        return self.__status_topic

    def get_abs_topic(self, *relative_topic: str) -> str:
        return '/'.join([self.__base_topic] + list(relative_topic))

    def __publish_status(self, status: str) -> None:
        if status == self.__published_status:
            return

        _LOGGER.info('Publish status {!r}'.format(status))
        self.publish_single(self.__status_topic, status, retain=True)

        self.__published_status = status

    def publish_online_status(self) -> None:
        self.__publish_status('online')

    def publish_offline_status(self) -> None:
        self.__publish_status('offline')


def main():
<<<<<<< HEAD
    ups = apc.parse(apc.get(host=APCUPSD_HOST))
    HOSTNAME = ups.get('HOSTNAME', 'apcupsd-mqtt')
    MQTT_TOPIC_PREFIX = MQTT_TOPIC + "/mqtt:" + UPS_ALIAS + "/feature/mqtt:"

    first_run = True
    logger.info("Printing first submission for debug purposes:")

    result = pyfiglet.figlet_format("apcupsd-mqtt")
    print( result )
    while True:
        ups_data = apc.parse(apc.get(host=APCUPSD_HOST), strip_units=True)
        try:
            max_watts = float(ups_data.get('NOMPOWER', 0.0))
            current_percent = float(ups_data.get('LOADPCT', 0.0))
            current_watts = ((max_watts*current_percent)/100)
            ups_data['WATTS'] = current_watts

        except:
            logger.error("unable to conjure up the watts. @brandon you're bad at maths.")

        for k in ups_data:
            topic_id = MQTT_TOPIC_PREFIX + str(k) + "/state"
            if first_run:
                logger.info("%s = %s" % (topic_id, str(ups_data[k])))
            pub_mqtt( topic_id, str(ups_data[k]) )
        if first_run:
            logger.info("end first_run debug")
            first_run = False
        time.sleep(INTERVAL)
=======
    global exiting_main_loop

    debug_logging = os.getenv('DEBUG', '0') == '1'
    mqtt_port = int(os.getenv('MQTT_PORT', 1883))
    mqtt_host = os.getenv('MQTT_HOST', 'localhost')
    mqtt_user = os.getenv('MQTT_USER')
    mqtt_password = os.getenv('MQTT_PASSWORD')

    mqtt_auth = {'username': mqtt_user, 'password': mqtt_password} if mqtt_user and mqtt_password else None

    interval = int(os.getenv('APCUPSD_INTERVAL', 10))
    alias = os.getenv('UPS_ALIAS', '')
    apcupsd_host = os.getenv('APCUPSD_HOST', '127.0.0.1')

    configure_logging(debug_logging)

    _LOGGER.info('Get initial data from UPS... {!r}'.format(apcupsd_host))
    ups = apc.parse(apc.get(host=apcupsd_host))

    serial_no = ups.get('SERIALNO', '000000000000')
    model = ups.get('MODEL', 'Unknown')
    firmware = ups.get('FIRMWARE', 'FW 000.00')

    if not alias:
        alias = serial_no

    mqtt_client = HaCapableMqttClient(
        '{}/{}'.format(MQTT_TOPIC, alias),
        broker_host=mqtt_host,
        broker_port=mqtt_port,
        broker_auth=mqtt_auth
    )

    mqtt_topic = mqtt_client.get_abs_topic('ups')
    config = Config(serial_no, alias, model, firmware, mqtt_topic, mqtt_client.status_topic)

    _LOGGER.info('Configuring Home Assistant via MQTT Discovery... {}:{}'.format(mqtt_host, mqtt_port))

    discovery_msgs = [
        {
            'topic': sensor.topic,
            'payload': json.dumps(sensor.payload, sort_keys=True),
            'retain': True,
        }
        for sensor in config.sensors
    ]
    mqtt_client.publish_multiple(discovery_msgs)

    _LOGGER.info('Starting value updater loop...')

    signal.signal(signal.SIGINT, stop_main_loop)
    signal.signal(signal.SIGTERM, stop_main_loop)

    exiting_main_loop = False
    try:
        while True:
            main_loop(apcupsd_host, mqtt_client, mqtt_topic)

            for _ in range(interval * 2):
                time.sleep(0.5)

                if exiting_main_loop:
                    exit(0)

    finally:
        mqtt_client.publish_offline_status()


class LevelFilter(logging.Filter):
    def __init__(self, filtered_level: int, **kwargs):
        self.__filtered_level = filtered_level

        super().__init__(**kwargs)

    def filter(self, record: logging.LogRecord):
        return record.levelno == self.__filtered_level


def configure_logging(debug_logging: bool) -> None:
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.DEBUG)
    stderr_handler.addFilter(LevelFilter(logging.DEBUG))

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    logging.basicConfig(
        format='%(message)s',
        level=logging.DEBUG if debug_logging else logging.INFO,
        handlers=[stdout_handler, stderr_handler]
    )


def stop_main_loop(*args) -> None:
    global exiting_main_loop

    exiting_main_loop = True


def main_loop(apcupsd_host: str, mqtt_client: HaCapableMqttClient, mqtt_topic: str) -> None:
    try:
        ups_data = apc.parse(apc.get(host=apcupsd_host), strip_units=True)
    except Exception as e:
        message = repr(e)

        if isinstance(e, OSError) and 'No route to host' in message:
            message = '{} ({})'.format(message, apcupsd_host)

        _LOGGER.error('ERROR: '.format(message), exc_info=False)
        mqtt_client.publish_offline_status()

        return

    status = {
        key.lower(): str(value)
        for key, value in ups_data.items()
    }

    status_string = json.dumps(status, sort_keys=True)
    _LOGGER.debug(status_string)

    mqtt_client.publish_single(mqtt_topic, status_string)
    mqtt_client.publish_online_status()
>>>>>>> c4b141a79bd293e1ec23ceae1025acfcc5d5ba71


if __name__ == '__main__':
    main()
