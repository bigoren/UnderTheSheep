import requests
import paho.mqtt.client as mqtt
import json

#print ("start")
#payload = {'file_id': 'Music/alterego.wav', 'start_offset_ms': 0}
#r = requests.put("http://10.0.0.200:8080/api/current-song", json=payload)
#print ("sent")
#print (r.status_code)
#
#print (r.content)


broker_url = "10.0.0.200"
broker_port = 1883

def on_connect(client, userdata, flags, rc):
   print("Connected With Result Code " (rc))

def on_disconnect(client, userdata, rc):
   print("Client Got Disconnected")

def on_message(client, userdata, message):
   print("Sensor Message Recieved: "+message.payload.decode())

def on_message_monitor(client, userdata, message):
   print("Monitor Message Recieved: "+message.payload.decode())

def on_message_player(client, userdata, message):
   print("Player Message Recieved: "+message.payload.decode())
   payload = json.loads(message.payload)
   if (not payload["song_is_playing"]):
      print("Song is not playing, send play message")
      player_msg = {'file_id': 'alterego.wav', 'start_offset_ms': 0}
      r = requests.put("http://10.0.0.200:8080/api/current-song", json=player_msg)
      print (r.status_code)
      print(r.content)


client = mqtt.Client(client_id="main")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(broker_url, broker_port)

client.subscribe("monitor",0)
client.subscribe("/sensors/loadcell/#",0)
client.subscribe("current-song",0)
#client.subscribe([(‘monitor’, 0),(‘sensors/loadcell/*’, 0)])

client.message_callback_add("monitor", on_message_monitor)
client.message_callback_add("current-song", on_message_player)

client.will_set("monitor","Main control is down",0,retain=False)

client.publish(topic="monitor", payload="Main control python up", qos=0, retain=False)

client.loop_forever()
