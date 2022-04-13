import os
import json
import random
import time
import paho.mqtt.client as mqtt

speed_factor = 10

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Tickgen connected to Broker")

        global Connected 
        Connected = True
    else:
        print("Tickgen connection failed")

def on_message(client, userdata, message):
    speed_factor = message.payload

Connected = False

mqttAddr = os.getenv('MQTT_ADDR', 'localhost')

print(f"Talking to \"{mqttAddr}\" as Broker")

time.sleep(10)
client = mqtt.Client("Tickgen")
client.on_connect = on_connect 
client.on_message = on_message

client.connect(host=mqttAddr, port=1883)
client.loop_start()

while Connected != True:
    time.sleep(0.1)

time.sleep(20)
client.publish(f"tickgen/tick", 1)
client.publish(f"tickgen/speed_factor", speed_factor)

client.subscribe("tickgen/speed_factor", 1)

while True:
    print(time.localtime())
    client.publish(f"tickgen/tick", 1)
    client.publish(f"tickgen/speed_factor", speed_factor)
    time.sleep(speed_factor)