import asyncio
import aiomqtt
import logging
import os
import subprocess

# Configure Logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s.%(msecs)03d] -%(levelname).1s- : %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')
logging.info('Watchdog for UnderTheSheep')

class Watchdog:

    def __init__(self, _loop, mqtt_client, timeout_minute=15):
        self._timeout_minute = timeout_minute
        self._timeout_timer = None
        self._loop = loop
        self.mqtt_client = mqtt_client
        self.timeout_finished()

    def mqtt_sub(self):
        self.mqtt_client.subscribe("current-song", 1)
        self.mqtt_client.message_callback_add("current-song", self._on_message_player)

    def _on_message_player(self, client, userdata, message):
        if self._timeout_timer is not None:
            logging.info("Song request received, Canceling timer")
            self._timeout_timer.cancel()
            self._timeout_timer = None

        self._timeout_timer = self._loop.call_later(60 * self._timeout_minute, self.timeout_finished)
    
    def timeout_finished(self):
        logging.info("Timeout reached")
        os.system("pkill -f main.py")
        os.system("setsid python3 main.py > output.log 2>&1 &")
        self._timeout_timer = self._loop.call_later(60 * self._timeout_minute, self.timeout_finished)


loop = asyncio.get_event_loop()
broker_url = "10.0.0.200"
broker_port = 1883

mqtt_c = aiomqtt.Client(loop=loop, client_id="watchdog")
watchdog = Watchdog(loop, mqtt_c)

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

    mqtt_c.message_callback_add("monitor", on_message_monitor)
    watchdog.mqtt_sub()


loop.run_until_complete(subscribe())

loop.run_forever()

