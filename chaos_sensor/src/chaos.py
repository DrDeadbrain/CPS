import os
import json
import random
import time
import calendar
from datetime import datetime
import paho.mqtt.client as mqtt


def on_message(client, userdata, message):
    print("Sending chaos data")
    global Lastval
    Lastval = random.randrange(4000, 8500)
    Lastval = Lastval * .3 + getRandom() * .7

    currentGMT = time.gmtime()
    ts = calendar.timegm(currentGMT)
    dt = datetime.fromtimestamp(ts)
    #data = {"payload": {Lastval}, "timestamp": "{dt}"}
    client.publish(f"sensor/{sensorID}/data", json.dumps({"payload": Lastval, "timestamp": dt}, indent=4, sort_keys=True, default=str))

def getRandom() -> int:
    return random.randrange(500, 8500)

#Connected = False
sensorID = os.getenv('Sensor_ID', '1')
mqttAddr = os.getenv('MQTT_ADDR', 'localhost')

time.sleep(10)

client = mqtt.Client()
#client.on_connect = on_connect
client.on_message = on_message
 
client.connect(host=mqttAddr, port=1883)
client.loop_start()

#while Connected != True:
#    time.sleep(0.1)

client.publish(f"sensor/{sensorID}", json.dumps({"type": "Fake Sensor"}), qos=1, retain=True)

client.subscribe(f"tickgen/tick", 1)



while True:
    time.sleep(0.1)
#    print("Sending chaos data")
#    Lastval = Lastval * .3 + getRandom() * .7
#    client.publish(f"sensor/{sensorID}/data", json.dumps({lastVal}))
#    time.sleep(10)
