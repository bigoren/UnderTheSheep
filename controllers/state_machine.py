import asyncio

from aiohttp import ClientSession

from controllers.song import Song
from controllers.wait_players import WaitPlayers
from controllers.wait_stage import WaitStage
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
        self._stage.register_on_disconnected_event(self.stage_disconnected_event)

        self._boxes = boxes
        self._boxes.register_on_chip_event(self.boxes_chip_event)
        self._boxes.register_on_disconnected_event(self.boxes_disconnected_event)

        self._Song_state = Song(self._loop, self.audio_service, self.start_state_wait_for_players)

        self.curr_state = None
        #self._loop.call_later(3, self.start_state_wait_for_players)

    def stage_full_event(self, is_full):
        if (self.curr_state != None) and (type(self.curr_state) != Song):
            self.curr_state.stage_full_event(is_full)

    def stage_disconnected_event(self):
        if type(self.curr_state) != Song:
            self.start_state_play_song()

    def boxes_chip_event(self, msg_data, box_index):
        if type(self.curr_state) != WaitStage:
            self.curr_state.boxes_chip_event(msg_data, box_index)

    def boxes_disconnected_event(self):
        if type(self.curr_state) != Song:
            self.start_state_play_song()

    def start_state_play_song(self):
        print("start_state_play_song")
        self.curr_state = self._Song_state
        self.curr_state.choose_song()

    def start_state_wait_for_players(self):
        print("start_state_wait_for_players")
        self.players_service = Players()
        self.curr_state = WaitPlayers(self._loop, self.audio_service, self._boxes, self.players_service, self._stage,
                                      self.start_state_play_song, self.start_state_wait_for_stage)

    def start_state_wait_for_stage(self):
        print("start_state_wait_for_stage")
        self.curr_state = WaitStage(self._loop, self.audio_service, self._stage,
                                    self.start_state_play_song, self.start_state_wait_for_stage)

    def start_state_game_on(self):
        # self.curr_state = GameOn(self._loop, self.audio_service, self._boxex, self.players_service, self._stage,
        #                             self.start_state_play_song)
        pass

    def on_all_chips_received(self):
        self._loop.call_soon(self.start_state_wait_for_stage)

