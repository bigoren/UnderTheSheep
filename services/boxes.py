import datetime
import json
import logging
import csv


class BoxData:

    def __init__(self):
        self.color = None
        self.uid = None


class Boxes:
    total_box_number = 3

    def __init__(self, loop, mqtt_client):

        # None means no comm with box
        self.mqtt_client = mqtt_client

        self.boxes = {i: False for i in range(1, self.total_box_number + 1)}
        self.box_color = [None] * self.total_box_number
        self.curr_uid = [None] * self.total_box_number
        self.old_chip = [None] * self.total_box_number
        self._on_chip_event = None
        self._on_disconnected_event = None
        self._loop = loop
        self._chips_log = open(datetime.datetime.now().strftime('chips_%Y-%m-%d_%H-%M'), 'w', newline='')
        self._csv_writer = csv.writer(self._chips_log, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        self._csv_writer.writerow(["Chip UID", "Old Chip", "Box Id", "State"])

    def log_chip(self, chip_uid, is_old_chip, box_id, current_state_name):
        self._csv_writer.writerow([chip_uid, is_old_chip, box_id, current_state_name])
        self._chips_log.flush()

    def mqtt_sub(self):
        self.mqtt_client.subscribe("/sensors/rfid/+/monitor", 0)
        self.mqtt_client.subscribe("/sensors/rfid/+/chip", 0)
        self.mqtt_client.message_callback_add("/sensors/rfid/+/monitor", self._on_mqtt_message_monitor)
        self.mqtt_client.message_callback_add("/sensors/rfid/+/chip", self._on_mqtt_message_chip)

    def get_alive(self):
        return [k for k, v in self.boxes.items() if v]

    def _on_mqtt_message_monitor(self, client, userdata, message):
        logging.debug("Got message: {}/{}".format(message.topic, message.payload.decode()))
        box_name = message.topic.split("/")[3]
        box_index = int(box_name[3])
        msg_data = json.loads(message.payload.decode())
        self._new_monitor_message(msg_data, box_index)

    def _on_mqtt_message_chip(self, client, userdata, message):
        logging.debug("Got message: {} {}".format(message.topic, message.payload.decode()))
        box_name = message.topic.split("/")[3]
        box_index = int(box_name[3])
        msg_data = json.loads(message.payload.decode())
        self._new_chip_message(msg_data, box_index)

    def _new_monitor_message(self, msg_data, box_index):
        if msg_data["alive"]:
            self.boxes[box_index] = True
        else:
            if self.boxes[box_index] is True:
                self._handle_dead(box_index)

    def _new_chip_message(self, msg_data, box_index):
        self.call_chip_event(msg_data, box_index)

    def _handle_dead(self, box_index):
        logging.warning("box is disconnected")
        self.boxes[box_index] = False
        self.call_disconnected_event()

    def send_command_to_leds(self, box_index, color):
        topic = "/sensors/rfid/box{0}/leds".format(box_index)
        # color map = 0 is off, 1 is red, 2 is yellow, 3 is green, 4 is blue, 5 is purple, 6 is rainbow, 7 is twinkly
        # color > 127 is rainbow, master state 0 is off, 1 is twinkly, 2 is colors
        if color:
            if color == 6:
                data = {"color":128, "master_state":2}
            elif color == 7:
                data = {"color":128, "master_state":1}
            else:
                data = {"color":color, "master_state":2}
        else:
            data = {"color":128, "master_state":0}
        json_str = json.dumps(data)
        #logging.debug("sending command to leds on topic {0}, msg: {1}".format(topic, json_str))
        self.mqtt_client.publish(topic, json_str)

    def shutdown_all_leds(self):
        for box_index in self.boxes.keys():
            self.send_command_to_leds(box_index, None)

    def waiting_for_players_led(self):
        for box_index in self.boxes.keys():
            self.send_command_to_leds(box_index, 7)

    def register_on_chip_event(self, func):
        self._on_chip_event = func

    def register_on_disconnected_event(self, func):
        self._on_disconnected_event = func

    def call_chip_event(self, msg_data, box_index):
        if self._on_chip_event:
            self._loop.call_soon(self._on_chip_event, msg_data, box_index)

    def call_disconnected_event(self):
        if self._on_disconnected_event:
            self._loop.call_soon(self._on_disconnected_event)
