import asyncio

from aiohttp import ClientSession

from controllers.song import Song
from controllers.wait_players import WaitPlayers
from services.players import Players


class UnderTheSeaState:
    play_song = "playing_song"
    wait_for_players = "wait_for_players"
    wait_for_stage = "wait_for_stage"
    game_on = "game_on"

    def __init__(self, loop, stage, boxes, audio_service):
        self._loop = loop
        self.audio_service = audio_service
        self.state_handlers = []
        self.players_service = None

        self._stage = stage
        self._stage.register_on_full_event(self.stage_full_event)

        self._boxes = boxes
        self._boxes.register_on_chip_event(self.boxes_chip_event)
        self._boxes.register_on_disconnected_event(self.boxes_disconnected_event)

        self._Song_state = Song(self._loop, self.audio_service, self.start_state_wait_for_players)

        self.curr_state = None
        self._loop.call_later(3, self.start_state_wait_for_players)

    def stage_full_event(self, is_full):
        pass

    def boxes_chip_event(self, msg_data, box_index):
        if self.curr_state:
            self.curr_state.boxes_chip_event(msg_data, box_index)

    def boxes_disconnected_event(self):
        if self.curr_state:
            self.curr_state.boxes_disconnected_event()

    def song_ended(self):
        pass

    def start_state_play_song(self):
        print("start_state_play_song")
        self.curr_state = self._Song_state
        self.curr_state.choose_song()

    def start_state_wait_for_players(self):
        print("start_state_wait_for_players")
        self.players_service = Players()
        self.curr_state = WaitPlayers(self._loop, self.audio_service, self._boxes, self.players_service,
                                      self.start_state_play_song, self.start_state_wait_for_stage)

    def start_state_wait_for_stage(self):
        print("start_state_wait_for_stage")
        self.change_state(self.wait_for_stage)
        # asyncio.create_task(self.play_song_request("call_for_stage.wav"))
        # self.state_handlers.append(self._loop.call_later(30, self.start_state_play_song))
        # self.state_handlers.append(self._loop.call_later(15, self.play_song_request, "call_again_for_stage.wav"))
        # self._stage.register_on_full(self.start_state_game_on)

    def start_state_game_on(self):
        self.change_state(self.game_on)

    def change_state(self, new_state):
        pass

    def on_all_chips_received(self):
        self._loop.call_soon(self.start_state_wait_for_stage)
        self.change_state(self.wait_for_stage)

