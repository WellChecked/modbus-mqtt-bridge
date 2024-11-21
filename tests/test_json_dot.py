import json
from jsonpath_ng import parse


def get_message():
    data = {
        "sitename": "device123",
        "component": "tank",
        "timestamp": 1732048080.0006711,
        "incoming": "20241119102500_WellOne",
        "processed": {
            "flow": 95.56933,
            "counted": 1600,
            "calculated": 800,
            "uptime": 1,
            "files": [
                "g_tank_20241119142800.mp4",
                "g_tank_20241119142800.png"
            ]
        },
        "s3_object_keys": [
            "g_tank_20241119142800.png",
            "g_tank_20241119142800.mp4"
        ]
    }
    return data


if __name__ == '__main__':
    flow_expr = parse('processed.flow')
    uptime_expr = parse('processed.uptime')

    message = get_message()
    match = flow_expr.find(message)
    if match:
        value = match[0].value
        print(f"flow = {value}")

    match = uptime_expr.find(message)
    if match:
        value = match[0].value
        print(f"uptime = {value}")
