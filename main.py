#!/usr/bin/env python3.7
import asyncio
import aiomqtt
import logging
import logging.handlers
import os

from services.audio import AudioService
from services.boxes import Boxes
from services.stage import Stage
from controllers.state_machine import UnderTheSeaState

# Configure Logging
logfile = 'under_the_sheep.log'
log_formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] -%(levelname).1s- : %(message)s',
                                  datefmt='%d-%m-%Y %H:%M:%S')
# set logging to file to be a 100MB file with 1 rotated backup
file_handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=100e6, backupCount=1)
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

root_logger.setLevel(logging.DEBUG)

logging.info('Main program started for UnderTheSheep.')
logging.info('Log file: {}'.format(os.path.abspath(logfile)))
loop = asyncio.get_event_loop()
broker_url = "192.168.14.22"
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
        logging.info('subscribe(): on_connect(): connected with result code: {}'.format(rc))
        connected.set()
        # state_machine.start_state_wait_for_players()

    mqtt_c.on_connect = on_connect

    logging.info(f'Connecting to: {broker_url}:{broker_port}')
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

loop.run_forever()

