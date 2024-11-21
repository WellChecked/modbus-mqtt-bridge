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

NOTE: Since the default modbus port is less than 1024, most systems will report back 
a permission failure when trying to bind the modbus tcp server to the address and port.  
To get around this, either:

- start the service as an administrator account (i.e. root on linux),
- change the port to a port greater than 1024 (1502 as an example).

## Configuration

### File

* CONFIG_FILE = os.getenv('CONFIG_FILE', 'config/registers.json')

### Register Definitions

```json
[
  {
    "topic": "system/status",
    "jsonpath": "random",
    "register": 41001,
    "type": "float"
  },
  {
    "topic": "system/status",
    "jsonpath": "cpu.percent",
    "register": 41003,
    "type": "float"
  },
  {
    "topic": "system/status",
    "jsonpath": "cpu.load_average.load_1m",
    "register": 41005,
    "type": "float"
  },
  {
    "topic": "system/status",
    "jsonpath": "cpu.load_average.load_5m",
    "register": 41007,
    "type": "float"
  },
  {
    "topic": "system/status",
    "jsonpath": "cpu.load_average.load_15m",
    "register": 41009,
    "type": "float"
  },
  {
    "topic": "system/status",
    "jsonpath": "memory.swap.used",
    "register": 41011,
    "type": "float",
    "getter": ":value / 1000000000"
  },
  {
    "topic": "system/status",
    "jsonpath": "memory.virtual.used",
    "register": 41013,
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

## Tools

### MQTT Viewers

- [MQTT Explorer](https://mqtt-explorer.com/)
- [MQTTX](https://mqttx.app/)

### Modbus Clients

#### Windows

- [Modbus Poll](https://www.modbustools.com/download.html)

#### Mac

- [ModbusTcpClient](https://apps.apple.com/hr/app/modbus-tcp-client/id1635888824?mt=12)

#### Linux

- [Modpoll](https://www.modbusdriver.com/modpoll.html)

## Python

### Environment

```aiignore
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install -r requirements.txt 
```

### Test data

In order to test locally, a docker compose is made available to start a mosquitto mqtt broker 
that allows anonymous logins.  The brider_testdata.py script by default can publish data to 
this broker for testing.

```aiignore
$ docker compose up -d 
```
After the broker is started, the script 'bridge_testdata.py' can be ran to generate test data
to the broker.  The publish topic is 'system/status' which you will notice matches the 
topics within the 'config/registers.json' file.

```aiignore
$ python3 bridge_testdata.py
```

### Run

The defaults for bridge.py will startup assuming a local mqtt broker with anonymous logins.

```aiignore
$ python3 bridge.py
```
NOTE: the broker.py script must be started in the root of the project since it is assuming
the configuration is in './config' directory.

## Docker

```aiignore
$ docker run -t wcsi/modbus-mqtt-bridge \
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
    image: wcsi/modbus-mqtt-bridge
    container_name: modbus-bridge
    ports:
      - 502:502
    environment:
      - MQTT_HOSTNAME=<mqtt_host>
      - MQTT_PORT=<mqtt_port>
      - MQTT_USERNAME=<mqtt_user>
      - MQTT_PASSWORD=<mqtt_pass>
      - MQTT_TOPIC_PREFIX=<mqtt_topic_prefix>
      - CONFIG_FILE=<configuration_json_filename>
      - MODBUS_PORT=<modbus_port>
    volumes:
      - ./config:/app/config
```
The topic prefix is prepending to every topic found within the registers configuration json file.
