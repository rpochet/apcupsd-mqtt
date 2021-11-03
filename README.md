# APCUPSD to MQTT

- Publish APCUPSD data to MQTT
- Home Assistant integration with auto-discovery


## Environment variables

- ``APCUPSD_HOST`` hostname or IP address of the `apcupsd` (default: `127.0.0.1`)
- ``UPS_ALIAS`` device name (default: _device serial_)
- ``APCUPSD_INTERVAL`` refresh interval in seconds (default: `10`)
- ``MQTT_HOST`` MQTT server  (default: `localhost`)
- ``MQTT_PORT`` MQTT server hostname or IP address (default: `1883`)
- ``MQTT_USER`` MQTT auth user (optional)
- ``MQTT_PASSWORD`` MQTT auth password (optional)
