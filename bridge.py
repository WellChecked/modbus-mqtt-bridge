import click
import main


@click.command()
@click.option('--hostname', default='localhost',
              help='The hostname or IP address of the MQTT server.')
@click.option('--port', default=1883,
              help='The port of the MQTT server.')
@click.option('--username', default=None,
              help='The username to authenticate to the MQTT server.')
@click.option('--password', default=None,
              help='The password to authenticate to the MQTT server.')
@click.option('--mqtt_topic_prefix', default=None,
              help='A prefix for published MQTT topics.')
@click.option('--modbus_host', default='0.0.0.0',
              help='The bind host of the Modbus server.')
@click.option('--modbus_port', default=502,
              help='The bind port of the Modbus server.')
@click.option('--config', default='./config/registers.json',
              help='The JSON config file for your modbus server.')
def bridge(
        hostname: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        mqtt_topic_prefix: str = None,
        modbus_host: str = None,
        modbus_port: int = None,
        config: str = None
):
    main.main(
        hostname=hostname, port=port, username=username, password=password, mqtt_topic_prefix=mqtt_topic_prefix,
        modbus_host=modbus_host, modbus_port=modbus_port,
        config=config
    )
    return


if __name__ == '__main__':
    bridge()
