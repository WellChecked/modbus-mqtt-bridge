# modbus-mqtt-bridge
Modbus to MQTT bridge

## Overview
This is project was built to bridge MQTT topic data with Modbus registers
using the [Modbus TCP Server.](https://pypi.org/project/modbus-tcp-server/) 
and then extending a BaseDataSource to include [mqtt topic subscriptions](https://pypi.org/project/paho-mqtt/).

## Environment 

* MQTT_HOSTNAME = os.getenv('MQTT_HOSTNAME')
* MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
* MQTT_USERNAME = os.getenv('MQTT_USERNAME')
* MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
* MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX')


* MODBUS_BIND_IP = os.getenv('MODBUS_BIND_IP', '0.0.0.0')
* MODBUS_PORT = int(os.getenv('MODBUS_PORT', 502))

## Configuration

### File

* CONFIG_FILE = os.getenv('CONFIG_FILE', 'config/registers.json')

### Register Definitions

```json
[
  {
    "topic": "bridge123/up/system",
    "jsonpath": "cpu.percent",
    "register": 41004,
    "type": "float"
  },
  {
    "topic": "bridge123/up/system",
    "jsonpath": "cpu.load_average.load_1m",
    "register": 41006,
    "type": "float"
  },
  {
    "topic": "bridge123/up/system",
    "jsonpath": "cpu.load_average.load_5m",
    "register": 41008,
    "type": "float"
  },
  {
    "topic": "bridge123/up/system",
    "jsonpath": "cpu.load_average.load_15m",
    "register": 41010,
    "type": "float"
  },
  {
    "topic": "bridge123/up/system",
    "jsonpath": "memory.swap.used",
    "register": 41012,
    "type": "float",
    "getter": ":value / 1000000000"
  },
  {
    "topic": "bridge123/up/system",
    "jsonpath": "memory.virtual.used",
    "register": 41014,
    "type": "float",
    "getter": ":value / 1000000000"
  }
]
```

### Topic

The topics found in the configuration file are used to create mqtt 
subscriptions.  MQTT wildcards are valid within topic references.

### Json path

The [jsonpath](https://pypi.org/project/jsonpath-ng/) configuration is a jsonpath expression used to search a json document found 
at a topic.  

### Getters

A getter is an eval expression using string replacement of the value pulled from
json document.  This can be used to scale values up or down. 

### Value Type

* int16, uint16 - This value fits within a single modbus register.
* int32, uint32 - This value requires 2 registers in order to return the value.
* float - This value requires 2 modbus registers in order to return a value.

## Python 

```aiignore
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install -r requirements.txt 
$ python3 bridge.py

```

## Docker

```aiignore
$ docker run -t wcsi/zen-modbus-mqtt-bridge \
    -p 1502:502 -v ./config/registers.json:/app/config --env-file vars.env 
```
**vars.env** 

```aiignore
MQTT_HOSTNAME=<mqtt_host>
MQTT_PORT=<mqtt_port>
MQTT_USERNAME=<mqtt_username>
MQTT_PASSWORD=<mqtt_password>
MQTT_TOPIC_PREFIX=<mqtt_topic_prefix>
CONFIG_FILE=/app/config/registers.json
MODBUS_PORT=<modbus_tcp_port>
```
## docker-compose.yml

```aiignore
services:
  bridge:
    image: wcsi/zen-modbus-mqtt-bridge
    container_name: modbus-bridge
    ports:
      - 502:502
    environment:
      - MQTT_HOSTNAME=mqtt.edgestack.io
      - MQTT_PORT=1883
      - MQTT_USERNAME=org123.client
      - MQTT_PASSWORD=password
      - MQTT_TOPIC_PREFIX=data/org123
      - CONFIG_FILE=config/registers.json
      - MODBUS_PORT=1502
    volumes:
      - ./config:/app/config
```