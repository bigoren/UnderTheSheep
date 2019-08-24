import asyncio
import aiomqtt
import logging

from services.audio import AudioService
from services.boxes import Boxes
from services.stage import Stage
from controllers.state_machine import UnderTheSeaState

# Configure Logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s.%(msecs)03d] -%(levelname).1s- : %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')
logging.info('Main program started for UnderTheSheep.')

loop = asyncio.get_event_loop()
broker_url = "10.0.0.200"
broker_port = 1883

mqtt_c = aiomqtt.Client(loop=loop, client_id="main")

stage = Stage(loop, mqtt_c)
boxes = Boxes(loop, mqtt_c)
audio_service = AudioService(loop, mqtt_c)


async def subscribe():
    mqtt_c.loop_start()

    connected = asyncio.Event(loop=loop)

    def on_connect(client, userdata, flags, rc):
        logging.info('subscribe(): on_connect(): connected with result code: {}'.format(rc))
        connected.set()
        # state_machine.start_state_wait_for_players()

    mqtt_c.on_connect = on_connect

    logging.info("Connecting to: {}:{}".format(broker_url, broker_port))
    await mqtt_c.connect(broker_url, broker_port)
    await connected.wait()
    logging.info("Connected!")

    mqtt_c.subscribe("monitor", 0)

    def on_message_monitor(client, userdata, message):
        logging.debug("Monitor Message Received: " + message.payload.decode())

    audio_service.mqtt_sub()
    stage.mqtt_sub()
    boxes.mqtt_sub()

    mqtt_c.message_callback_add("monitor", on_message_monitor)


loop.run_until_complete(subscribe())

# We want to run the state machine only after we connected to the mqtt service
state_machine = UnderTheSeaState(loop, stage, boxes, audio_service)

loop.run_forever()

