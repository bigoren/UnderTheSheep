import json
import logging


class Stage:

    full_threshold = 350
    empty_threshold = 25

    def __init__(self, loop, mqtt_client):

        # None means no comm with stage
        self.mqtt_client = mqtt_client
        self.is_full = None

        self._on_full_event = None
        self._on_disconnected_event = None
        self._loop = loop
        self._show_reading = False

    def set_stage_show_reading(self, show_reading):
        self._show_reading = show_reading

    def get_is_full(self):
        return self.is_full

    def mqtt_sub(self):
        self.mqtt_client.subscribe("/sensors/loadcell/#", 0)
        self.mqtt_client.message_callback_add("/sensors/loadcell/load", self._on_message_load_cell)

    def get_is_alive(self):
        return self.is_full is not None

    def _new_message(self, curr_weight):
        if 'weight' not in curr_weight:
            self._handle_dead()
        else:
            self._handle_reading(int(curr_weight['weight']))

    def _on_message_load_cell(self, client, userdata, message):
        #logging.debug("Load Cell Message Received: " + message.payload.decode())
        self._new_message(json.loads(message.payload.decode()))

    def _handle_dead(self):
        logging.error("stage is disconnected")
        if self.is_full is not None:
            self.is_full = None
            self.call_full_event()
        self.call_disconnected_event()

    def _handle_reading(self, curr_weight):
        if self.is_full:
            curr_full = curr_weight > self.empty_threshold
        else:
            curr_full = curr_weight > self.full_threshold

        if curr_full != self.is_full:
            logging.info("full state changed. was: {0}, now: {1}".format(self.is_full, curr_full))
            self.is_full = curr_full
            self.call_full_event()

        if self._show_reading:
            if float(curr_weight) > self.empty_threshold:
                fill_percent = float(curr_weight) / float(self.full_threshold)
            else:
                fill_percent = 0
            self.send_command_to_leds(fill_percent)

    def send_command_to_leds(self, fill_percent, animation_mode=2, led_color=None):
        pub_topic = "/sensors/loadcell/leds"
        if fill_percent < 0:
            fill_percent = 0.0
        if fill_percent > 1:
            fill_percent = 1.0
        if led_color is None:
            led_color = int(fill_percent*128)
        data_out = {"animation_mode": animation_mode, "led_percent": fill_percent, "led_color": led_color}
        #logging.debug("sending {}".format(data_out))
        self.mqtt_client.publish(pub_topic, json.dumps(data_out))

    def register_on_full_event(self, func):
        self._on_full_event = func
        self.call_full_event()

    def call_full_event(self):
        if self._on_full_event is not None:
            logging.info("full event called, is full: {0}".format(self.is_full))
            self._loop.call_soon(self._on_full_event, self.is_full)

    def register_on_disconnected_event(self, func):
        self._on_disconnected_event = func

    def call_disconnected_event(self):
        if self._on_disconnected_event:
            self._loop.call_soon(self._on_disconnected_event)

