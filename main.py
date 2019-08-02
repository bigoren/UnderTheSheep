import asyncio
import json
import aiomqtt

from services.audio import AudioService
from services.boxes import Boxes
from services.stage import Stage
from controllers.state_machine import UnderTheSeaState

loop = asyncio.get_event_loop()
broker_url = "10.0.0.200"
broker_port = 1883

mqtt_c = aiomqtt.Client(loop=loop, client_id="main")

stage = Stage(loop, mqtt_c)
boxes = Boxes(loop, mqtt_c)
audio_service = AudioService(loop, mqtt_c)
state_machine = UnderTheSeaState(loop, stage, boxes, audio_service)



async def subscribe():
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

    def on_message_monitor(client, userdata, message):
        print("Monitor Message Received: " + message.payload.decode())

    audio_service.mqtt_sub()
    stage.mqtt_sub()
    boxes.mqtt_sub()

    mqtt_c.message_callback_add("monitor", on_message_monitor)


loop.run_until_complete(subscribe())

loop.run_forever()

