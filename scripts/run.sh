#!/usr/bin/env bash
echo "Create system network..."
docker network create cps-network

echo "Starting MQTT Broker..."
docker run -d -p 127.0.0.1:8883:1883 --net=cps-network --name mqttbroker \
    eclipse-mosquitto:2.0.14

#echo "Starting Tick Generator..."
#docker run -d --net=cps-network --name tick_gen tick_gen:0.1

echo "Starting dashboard..."
docker run -d -p 127.0.0.1:1880:1880 --net=cps-network --name dashboard dashboard:0.1

echo "Starting Chaos Sensor..."
docker run -d --net=cps-network --name chaos_sensor chaos_sensor:0.1