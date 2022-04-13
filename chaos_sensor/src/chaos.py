import os
import json
import random
import time
import paho.mqtt.client as mqtt

def getRandom() -> int:
    return random.randrange(500, 8500)

lastVal = random.randrange(4000, 8500)

mqttAddr = os.getenv('MQTT_ADDR', 'localhost')

print(f"Talking to \"{mqttAddr}\" as Broker")

time.sleep(10)
client = mqtt.Client()

client.connect(host=mqttAddr, port=1883)
client.loop_start()

client.publish(f"sensor/1", json.dumps({"type": "Fake Sensor"}), qos=1, retain=True)

while True:
    print("Sending chaos data")
    lastVal = lastVal * .3 + getRandom() * .7
    client.publish(f"sensor/1/data", json.dumps({"value": lastVal}), qos=1, retain=True)
    time.sleep(10)
