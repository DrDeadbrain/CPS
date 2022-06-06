# CPS

## Ohne Docker

### Node Red
#### *Node Red installieren*  
https://nodered.org/docs/getting-started/local  

Palette 'node-red-dashboard' installieren  
Menü - Palette verwalten - Installation  

#### *Node Red starten/stoppen:*  
```
cd ...\CPS\Praktikum\CPS\dashboard  
node-red  
```
```
Strg + c  
```

### MQTT Broker
#### *Mosquitto MQTT Broker installieren*  
https://mosquitto.org/download/  

#### *Config file (im Mosquitto-Ordner) anpassen (einfügen):*  

```
port 1880  
persistence false  
allow_anonymous true  
connection_messages true  
listener 1883  
listener 1884
```  

#### *Mosquitto starten/stoppen:* 
```
net start mosquitto  
net stop mosquitto
```
