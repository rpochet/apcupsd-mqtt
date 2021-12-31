# APCUPSD to MQTT

- Publish APCUPSD data to MQTT
- [Gladys](https://gladysassistant.com/) integration with Gladys


## Usage
  * Local `apcupsd` + local MQTT broker:
    ``` shell
    docker run -d              \
        --restart always       \
        --name 'apcupsd-mqtt'  \
        -e UPS_ALIAS='garage'  \
        ghcr.io/andras-tim/apcupsd-mqtt
    ```
  * Local `apcupsd` + remote MQTT broker + debug logs:
    ``` shell
    docker run -d                 \
        --restart always          \
        --name 'apcupsd-mqtt'     \
        -e UPS_ALIAS='garage'     \
        -e MQTT_HOST='mqtt.home'  \
        -e DEBUG=1                \
        ghcr.io/andras-tim/apcupsd-mqtt
    ```
  * Authentication required remote MQTT broker + remote `apcupsd`:
    ``` shell
    docker run -d                   \
        --restart always            \
        --name 'apcupsd-mqtt'       \
        -e UPS_ALIAS='garage'       \
        -e MQTT_HOST='mqtt.home'    \
        -e MQTT_USER='foo'          \
        -e MQTT_PASSWORD='bar'      \
        -e APCUPSD_HOST='apc.home'  \
        ghcr.io/andras-tim/apcupsd-mqtt
    ```

    _(MQTT over SSL is not supported yet)_

## Environment variables

- ``DEBUG`` print all queried values on STDOUT (_integer_, default: `0`)
- ``APCUPSD_HOST`` hostname or IP address of the `apcupsd` (_string_, default: `127.0.0.1`)
- ``UPS_ALIAS`` device name (_string_, default: _device serial_)
- ``APCUPSD_INTERVAL`` refresh interval in seconds (_integer_, default: `10`)
- ``MQTT_HOST`` MQTT broker  (_string_, default: `localhost`)
- ``MQTT_PORT`` MQTT broker hostname or IP address (_integer_, default: `1883`)
- ``MQTT_USER`` MQTT auth user (_optional string_)
- ``MQTT_PASSWORD`` MQTT auth password (_optional string_)
- ``MQTT_TOPIC`` MQTT root topic (_optional string_, default: `gladys/master/device`)
