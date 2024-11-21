import struct


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


# Example usage
float_value = 0.3
uint16_values = float_to_uint16(float_value)
value = uint16s_to_float(uint16_values[0], uint16_values[1])

print(hex(uint16_values[0]), hex(uint16_values[1]))
print(value)
