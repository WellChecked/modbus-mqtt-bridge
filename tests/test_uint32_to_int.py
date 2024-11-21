def uint32_to_uint16s(value):
    """Converts a uint32 value into two uint16 values."""
    high = (value >> 16) & 0xFFFF
    low = value & 0xFFFF
    return high, low


def uint16s_to_uint32(high, low):
    """Converts two uint16 values to a single uint32."""
    return (high << 16) | low


high_uint16 = 0x1234
low_uint16 = 0x5678

uint32_value = uint16s_to_uint32(high_uint16, low_uint16)
high, low = uint32_to_uint16s(uint32_value)

print(hex(high), hex(low))
print(hex(uint32_value))
