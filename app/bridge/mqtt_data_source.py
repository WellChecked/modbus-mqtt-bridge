import json
from enum import Enum
from typing import Any, List, Optional
from modbus_tcp_server.data_source import BaseDataSource
from paho.mqtt.matcher import MQTTMatcher
from pydantic import BaseModel

from app.bridge.mqtt_data_source_types import DataSourceTypeFactory
from app.helpers.logging_helpers import get_logger

log = get_logger(__name__)


class RegisterType(str, Enum):
    INT16 = "INT16"
    UINT16 = "UINT16"
    INT32 = "INT32"
    UINT32 = "UINT32"
    FLOAT = "FLOAT"


class Subscription(BaseModel):
    topic: str
    json_path: str
    json_path_expr: Any | None
    unit_id: int = 1
    register_address: int
    modbus_address: int
    register_type: RegisterType = RegisterType.UINT16
    getter: Optional[str] = None
    setter: Optional[str] = None


class MQTTDataSource(BaseDataSource):

    def __init__(self, subscriptions: List[Subscription]):
        self._mqtt_client = None
        self._subscriptions = {}
        self._subscription_registers = {}
        self._mqtt_matcher = MQTTMatcher()

        for subscription in subscriptions:
            if subscription.topic not in self._subscriptions:
                self._subscriptions[subscription.topic] = []
                self._mqtt_matcher[subscription.topic] = []

            # Data structures to manage incoming messages
            self._subscriptions[subscription.topic].append(subscription)
            self._mqtt_matcher[subscription.topic].append(subscription)

        self._holding_registers = {}

    def get_analog_input(self, unit_id: int, address: int) -> int:
        return 0

    def get_discrete_input(self, unit_id: int, address: int) -> bool:
        return False

    def get_holding_register(self, unit_id: int, address: int) -> int:
        if (unit_id, address) not in self._subscription_registers:
            print(f"No register for {(unit_id, address)}")

        register_value = self._holding_registers.get((unit_id, address), 0)
        print(f"Read {(unit_id, address)} = {register_value}")
        return register_value

    def get_coil(self, unit_id: int, address: int) -> bool:
        return True

    def set_holding_register(self, unit_id: int, address: int, value: int) -> None:
        pass

    def set_coil(self, unit_id: int, address: int, value: bool) -> None:
        pass

    def on_message(self, client, userdata, message):
        topic = message.topic
        for subscriptions in self._mqtt_matcher.iter_match(topic):
            json_data = message.payload.decode("utf-8")
            try:
                data = json.loads(json_data)
                for subscription in subscriptions:
                    log.debug(f"Trying to match [{subscription.json_path}]")
                    match = subscription.json_path_expr.find(data)
                    if match:
                        value = match[0].value
                        if value is not None:
                            data_source_type = DataSourceTypeFactory.get_data_source_type(
                                type_name=subscription.register_type,
                                getter=subscription.getter,
                                setter=subscription.setter
                            )
                            eval_value, register_values = data_source_type.to_registers(value=value)
                            log.debug(f"Received [{eval_value}] from [{subscription.json_path}]")
                            for i, register_value in enumerate(register_values, subscription.modbus_address):
                                log.debug(f"--Set [{hex(register_value)}] to {(subscription.unit_id, i)}")
                                self._holding_registers[(subscription.unit_id, i)] = (
                                    register_value
                                )
                    else:
                        log.debug(f"No match for [{subscription.json_path}]")

            except Exception as e:
                print(e)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print("Connected with result code " + str(reason_code))
        self._mqtt_client = client
        for topic, subscription in self._subscriptions.items():
            print(f"Subscribing to {topic}")
            client.subscribe(topic)

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        print("Disconnected with result code " + str(reason_code))
        for topic, subscription in self._subscriptions.items():
            print(f"Unsubscribing from {topic}")
            client.unsubscribe(topic)
