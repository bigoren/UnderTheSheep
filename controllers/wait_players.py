import asyncio

from controllers.controller import Controller


class WaitPlayers(Controller):

    seconds_for_giveup = 15
    seconds_for_recall = 5

    song_for_recall = "call_again.wav"
    song_call_for_players = "call_players.wav"

    def __init__(self, loop, audio_service, boxes_service, players_service, stage_service, giveup_cb, has_players_cb):
        super(WaitPlayers, self).__init__()

        self._loop = loop
        self._audio_service = audio_service
        self._boxes_service = boxes_service
        self._players_service = players_service
        self._stage_service = stage_service
        self._has_players_cb = has_players_cb
        self._giveup_cb = giveup_cb

        if not boxes_service.get_alive():
            print("not waiting for players - no connected boxes")
            self._loop.call_soon(self._giveup_cb)
            return

        if not stage_service.get_is_alive():
            print("not waiting for players - no connected stage")

        self._audio_service.play_song_request(self.song_call_for_players)
        self.reg_handlers.append(self._loop.call_later(self.seconds_for_giveup, self._state_timed_out))
        self.reg_handlers.append(self._loop.call_later(self.seconds_for_recall, self._audio_service.play_song_request, self.song_for_recall))

        self.registered_boxes = set()

    def _state_timed_out(self):
        if len(self.registered_boxes) > 0:
            self._loop.call_soon(self._has_players_cb)
        else:
            self._loop.call_soon(self._giveup_cb)

    def boxes_chip_event(self, msg_data, box_index):

        if box_index in self.registered_boxes:
            print("ignoring chip on an already registered box")
            return

        color = msg_data["color"]
        registered = self._players_service.register_player(msg_data["UID"], color, msg_data["old_chip"])
        if not registered:
            return

        self.registered_boxes.add(box_index)
        self._boxes_service.send_command_to_leds(box_index, color)
        self.check_if_done()

    def check_if_done(self):
        alive_boxes_indices = set(self._boxes_service.get_alive())
        if len(self.registered_boxes) >= len(alive_boxes_indices):
            self._loop.call_soon(self._has_players_cb)


