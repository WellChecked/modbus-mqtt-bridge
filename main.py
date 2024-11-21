import json
import os.path
import traceback
import uuid

from jsonpath_ng import parse
from jsonpath_ng.exceptions import JsonPathParserError
import paho.mqtt.client as mqtt
from modbus_tcp_server.network import ModbusTCPServer
from paho.mqtt.enums import CallbackAPIVersion

from app.bridge.mqtt_data_source import MQTTDataSource, RegisterType, Subscription


def load_subscriptions(mqtt_topic_prefix, config_file):
    if not os.path.exists(config_file):
        FileNotFoundError(f"{config_file} does not exist")

    with open(config_file, 'r') as f:
        subscriptions = []
        configurations = json.load(f)
        for configuration in configurations:
            topic = f"{os.path.join(mqtt_topic_prefix, configuration['topic'])}" if mqtt_topic_prefix else configuration['topic']
            try:
                register_address = int(configuration['register'])
                modbus_address = register_address - 40001
                subscriptions.append(Subscription(
                    topic=topic,
                    register_address=register_address,
                    modbus_address=modbus_address,
                    register_type=RegisterType(configuration['type'].upper()) if configuration['type'] else RegisterType.UINT16,
                    json_path=configuration['jsonpath'],
                    json_path_expr=parse(configuration['jsonpath']),
                    getter=configuration['getter'] if 'getter' in configuration else None,
                    setter=configuration['setter'] if 'setter' in configuration else None,
                ))
            except JsonPathParserError as e:
                print(f"Failed to parse {configuration['jsonpath']}")
                traceback.print_exc()

        return subscriptions


MQTT_HOSTNAME = os.getenv('MQTT_HOSTNAME')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX')
CONFIG_FILE = os.getenv('CONFIG_FILE', 'config/registers.json')
MODBUS_BIND_IP = os.getenv('MODBUS_BIND_IP', '0.0.0.0')
MODBUS_PORT = int(os.getenv('MODBUS_PORT', 502))


def main(
        hostname: str = MQTT_HOSTNAME,
        port: int = MQTT_PORT,
        username: str = MQTT_USERNAME,
        password: str = MQTT_PASSWORD,
        mqtt_topic_prefix: str = MQTT_TOPIC_PREFIX,
        modbus_host: str = MODBUS_BIND_IP,
        modbus_port: int = MODBUS_PORT,
        config: str = CONFIG_FILE
):
    subscriptions = load_subscriptions(mqtt_topic_prefix, config)
    data_source = MQTTDataSource(subscriptions=subscriptions)

    mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2)
    mqtt_client.on_message = data_source.on_message
    mqtt_client.on_connect = data_source.on_connect
    mqtt_client.on_disconnect = data_source.on_disconnect

    print(f"Connecting to MQTT broker using [{hostname}:{port}]")
    print(f"Binding on [{modbus_host}:{modbus_port}]")

    if username and password:
        mqtt_client.username_pw_set(username=username, password=password)
    mqtt_client.connect(host=hostname, port=port, keepalive=60)
    with ModbusTCPServer(modbus_host, modbus_port, data_source):
        try:
            mqtt_client.loop_forever(timeout=60, retry_first_connection=True)
        except KeyboardInterrupt:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()


if __name__ == '__main__':
    main()
