import struct
import numpy as np

from abc import ABC, abstractmethod
from typing import List, Union, Any, Tuple
from app.helpers.logging_helpers import get_logger

log = get_logger(__name__)


def uint32_to_uint16s(value):
    """Converts a uint32 value into two uint16 values."""
    high = (value >> 16) & 0xFFFF
    low = value & 0xFFFF
    return high, low


def uint16s_to_uint32(high, low):
    """Converts two uint16 values to a single uint32."""
    return (high << 16) | low


def float_to_uint16(value):
    """Converts a float to two uint16 values."""
    # Pack the float into a 4-byte binary representation
    packed_value = struct.pack('f', value)
    # Unpack the binary representation into two 2-byte unsigned integers
    uint16_values = struct.unpack('HH', packed_value)
    return uint16_values


def uint16s_to_float(uint16_1, uint16_2, precision: int = 5):
    """Converts two uint16 values to a float."""
    # Pack the two uint16 values into a bytes object
    packed_bytes = struct.pack('HH', uint16_1, uint16_2)
    # Unpack the bytes object as a float
    float_value = struct.unpack('f', packed_bytes)[0]
    return round(float(float_value), precision)


class DataSourceType(ABC):

    def __init__(self, setter: str, getter: str, unsigned: bool = False) -> None:
        self._setter = setter
        self._getter = getter
        self._unsigned = unsigned

    @abstractmethod
    def to_registers(self, value: Union[int, float]) -> Tuple[Any, List[int]]:
        pass

    @abstractmethod
    def from_registers(self, registers: List[int]) -> Union[int, float]:
        pass


class DataSourceTypeFactory:

    @classmethod
    def get_data_source_type(cls, type_name: str, getter: str, setter: str) -> DataSourceType:
        type_name = type_name.lower()
        log.debug(f"Getting data source type for {type_name}")
        if type_name.startswith("int16"):
            return Int16DataSourceType(getter=getter, setter=setter)
        elif type_name.startswith("uint16"):
            return Int16DataSourceType(getter=getter, setter=setter, unsigned=True)
        elif type_name.startswith("int32"):
            return Int32DataSourceType(getter=getter, setter=setter)
        elif type_name.startswith("uint32"):
            return Int32DataSourceType(getter=getter, setter=setter, unsigned=True)
        elif type_name.startswith("float"):
            return FloatDataSourceType(getter=getter, setter=setter)
        else:
            raise ValueError(f"Unsupported data source type: {type_name}")


class Int16DataSourceType(DataSourceType):

    def to_registers(self, value: Union[int, float]) -> Tuple[Any, List[int]]:
        value = np.uint16(value) if self._unsigned else np.int16(value)
        eval_value = eval(self._getter.replace(':value', str(value))) if self._getter else value
        return eval_value, [eval_value]

    def from_registers(self, registers: List[int]) -> Union[int, float]:
        eval_value: int = eval(self._setter.replace(':value', str(registers[0]))) if self._setter \
            else registers[0]
        return eval_value


class Int32DataSourceType(DataSourceType):

    def to_registers(self, value: Union[int, float]) -> Tuple[Any, List[int]]:
        value = np.uint32(value) if self._unsigned else np.int32(value)
        eval_value = eval(self._getter.replace(':value', str(value))) if self._getter else value
        high, low = uint32_to_uint16s(eval_value)
        return eval_value, [high, low]

    def from_registers(self, registers: List[int]) -> Union[int, float]:
        int32_value = uint16s_to_uint32(registers[0], registers[1])
        eval_value: int = eval(self._setter.replace(':value', str(int32_value))) if self._setter \
            else int32_value
        return eval_value


class FloatDataSourceType(DataSourceType):

    def __init__(self, setter: str = None, getter: str = None, unsigned: bool = False, precision: int = 5):
        super().__init__(setter=setter, getter=getter, unsigned=unsigned)
        self._precision = precision

    def to_registers(self, value: Union[int, float]) -> Tuple[Any, List[int]]:
        eval_value = round(eval(self._getter.replace(':value', str(value))), self._precision) \
            if self._getter else round(value, self._precision)
        high, low = float_to_uint16(eval_value)
        return eval_value, [high, low]

    def from_registers(self, registers: List[int]) -> Union[int, float]:
        float_value = uint16s_to_float(registers[0], registers[1])
        eval_value: float = float(eval(self._setter.replace(':value', str(float_value)))) if self._setter \
            else float_value
        return eval_value
