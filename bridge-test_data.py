import time
import json
import random

import click
import psutil
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from datetime import datetime


def cpu_status():
    cpu_percent = psutil.cpu_percent()
    load_average = psutil.getloadavg()
    return {
        "percent": cpu_percent,
        "load_average": {
            "load_1m": load_average[0],
            "load_5m": load_average[1],
            "load_15m": load_average[2]
        }
    }


def memory_status():
    swap = psutil.swap_memory()
    mem = psutil.virtual_memory()
    return {
        "swap": {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent,
            "sin": swap.sin,
            "sout": swap.sout
        },
        "virtual": {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
            "used": mem.used,
            "free": mem.free,
            "active": mem.active,
            "inactive": mem.inactive
        }
    }


def disk_status():
    disk_usages = []

    partitions = psutil.disk_partitions()
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disk_usages.append({
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "fstype": partition.fstype,
            "opts": partition.opts,
            "usage": {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            }
        })

    return disk_usages


def report_statuses(
        hostname: str = 'localhost',
        port: int = 1883,
        username: str = None,
        password: str = None,
        count: int = 12 * 5,
        delay: float = 5.0
):
    mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2)
    if username and password:
        mqtt_client.username_pw_set(username=username, password=password)
    mqtt_client.connect(host=hostname, port=port, keepalive=60)
    try:
        for i in range(count):
            _cpu_status = cpu_status()
            _memory_status = memory_status()
            _disk_status = disk_status()

            mqtt_client.publish(
                topic='system/status',
                payload=json.dumps({
                    "ts": time.time(),
                    "dt": datetime.isoformat(datetime.now()),
                    "did": "any_device_id",
                    "cpu": _cpu_status,
                    "memory": _memory_status,
                    # "disk": _disk_status,
                    "random": random.random() * 100.0,
                }),
                qos=0,
                retain=False
            )

            time.sleep(delay)

    finally:
        mqtt_client.disconnect()


@click.command()
@click.option('--hostname', default='localhost',
              help='The hostname or IP address of the MQTT server.')
@click.option('--port', default=1883,
              help='The port of the MQTT server.')
@click.option('--username', default=None,
              help='The username to authenticate to the MQTT server.')
@click.option('--password', default=None,
              help='The password to authenticate to the MQTT server.')
@click.option('--count', default=1883,
              help='The number of iterations to publish test data')
@click.option('--delay', default=5.0,
              help='The delay between publishing test data (in seconds)')
def main(
        hostname: str,
        port: int,
        username: str = None,
        password: str = None,
        count: int = 12 * 5,
        delay: float = 5.0
):
    report_statuses(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        count=count,
        delay=delay
    )


if __name__ == '__main__':
    main()
