from paho.mqtt.matcher import MQTTMatcher

matcher = MQTTMatcher()
matcher['foo/asd/#'] = 1
for value in matcher.iter_match('foo/bar'):
    print(value)
