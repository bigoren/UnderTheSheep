import asyncio
import json
import aiomqtt

from stage import Stage
from state_machine import UnderTheSeaState

loop = asyncio.get_event_loop()
broker_url = "10.0.0.200"
broker_port = 1883


stage = Stage(loop)
state_machine = UnderTheSeaState(stage)



async def subscribe():
    mqtt_c = aiomqtt.Client(loop=loop, client_id="main")
    mqtt_c.loop_start()

    connected = asyncio.Event(loop=loop)

    def on_connect(client, userdata, flags, rc):
        #print("Connected With Result Code "(rc))
        connected.set()

    mqtt_c.on_connect = on_connect

    await mqtt_c.connect(broker_url, broker_port)
    await connected.wait()
    print("Connected!")

    mqtt_c.subscribe("monitor", 0)
    mqtt_c.subscribe("/sensors/loadcell/#", 0)
    mqtt_c.subscribe("current-song", 0)

    def on_message(client, userdata, message):
        if message.topic == "/kivsee_box/1":
            parsed_msg = json.loads(message.payload)
            #on_chip(parsed_msg["chip_id"], parsed_msg["chip_color"])
        print("Got message:", message.topic, message.payload.decode())

    def on_message_monitor(client, userdata, message):
        print("Monitor Message Received: " + message.payload.decode())

    def on_message_load_cell(client, userdata, message):
        print("Load Cell Message Received: " + message.payload.decode())
        stage.new_reading(message.payload)

    def on_message_player(client, userdata, message):
        print("Player Message Received: " + message.payload.decode())
        payload = json.loads(message.payload)
        if not payload["song_is_playing"]:
            print("Song is not playing, change status")
            state_machine.song_ended()

    mqtt_c.message_callback_add("monitor", on_message_monitor)
    mqtt_c.message_callback_add("/sensors/loadcell/#", on_message_load_cell)
    mqtt_c.message_callback_add("current-song", on_message_player)


loop.run_until_complete(subscribe())

loop.run_forever()

