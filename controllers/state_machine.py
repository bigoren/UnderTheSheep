import logging
import asyncio

from aiohttp import ClientSession

from controllers.game import Game
from controllers.song import Song
from controllers.wait_players import WaitPlayers
from controllers.wait_stage import WaitStage
from services.players import Players


class UnderTheSeaState:
    play_song = "playing_song"
    wait_for_players = "/game_audio/call_players.wav"
    wait_for_stage = "wait_for_stage"
    game_on = "game_on"

    UID_TO_SONG = {
        "2c25bdfe": "lost.wav", # Ran
        "6e40cd61": "lost.wav", # Hadas
        "7eadcb61": "outlier.wav", # Loi
        "9e8ed461": "outlier.wav", # Gur
        "bebfc361": "useit.wav", # Amir
        "3e1fcd61": "millenium.wav", # Shani
        "2e78cd61": "because.wav", # Inbal
        "4c56b7fe": "nocturne.wav", # Bigler
        "e8acb61": "because.wav", # Eli
        "1ebcc461": "essoteric.wav", # Tili
        "fe7eca61": "because.wav", # Moli
        "7e8cc61": "fever.wav" # Ana
    }

    def __init__(self, loop, stage, boxes, audio_service):
        self._loop = loop
        self._audio_service = audio_service
        self.state_handlers = []
        self.players_service = None

        self._stage = stage
        self._stage.register_on_full_event(self.stage_full_event)
        self._stage.register_on_disconnected_event(self.stage_disconnected_event)
        self._audio_service.register_on_song_end_event(self._song_end_event)

        self._boxes = boxes
        self._boxes.register_on_chip_event(self.boxes_chip_event)
        self._boxes.register_on_disconnected_event(self.boxes_disconnected_event)

        self._Song_state = Song(self._loop, self._audio_service, self.start_state_wait_for_players)

        self.curr_state = None

        self.start_state_play_song()

    def stage_full_event(self, is_full):
        if (self.curr_state != None) and (type(self.curr_state) != Song):
            self.curr_state.stage_full_event(is_full)

    def stage_disconnected_event(self):
        logging.info("stage_disconnected_event")
        if type(self.curr_state) != Song:
            self.start_state_play_song()

    def _song_end_event(self):
        self.curr_state.song_end_event()

    def boxes_chip_event(self, msg_data, box_index):
        if not self.curr_state:
            return
        current_state_name = None
        if type(self.curr_state) != WaitStage:
            self.curr_state.boxes_chip_event(msg_data, box_index)

        if type(self.curr_state) == WaitStage:
            current_state_name = "WaitStage"
        elif type(self.curr_state) == Song:
            current_state_name = "Song"
            if msg_data["UID"] in self.UID_TO_SONG.keys():
                self.curr_state.choose_song(self.UID_TO_SONG[msg_data["UID"]])
        elif type(self.curr_state) == WaitPlayers:
            current_state_name = "WaitPlayers"
        elif type(self.curr_state) == Game:
            current_state_name = "Game"
        else:
            current_state_name = "NotCoded"

        self._boxes.log_chip(msg_data["UID"], msg_data["old_chip"], box_index, current_state_name)

    def boxes_disconnected_event(self):
        if type(self.curr_state) != Song:
            self.start_state_play_song()

    def cancel_prev_state(self):
        if self.curr_state is None:
            return
        self.curr_state.cancel_timers()

    def start_state_play_song(self):
        logging.info("start_state_play_song")
        self.cancel_prev_state()
        self.curr_state = self._Song_state
        self.curr_state.choose_song()
        self._boxes.shutdown_all_leds()
        self._stage.send_command_to_leds(animation_mode=0, fill_percent=0)

    def start_state_wait_for_players(self):
        self._boxes.shutdown_all_leds()
        logging.info("start_state_wait_for_players")
        self.players_service = Players()
        self.cancel_prev_state()
        self.curr_state = WaitPlayers(self._loop, self._audio_service, self._boxes, self.players_service, self._stage,
                                      self.start_state_play_song, self.start_state_wait_for_stage)

    def start_state_wait_for_stage(self):
        logging.info("start_state_wait_for_stage")
        self.cancel_prev_state()
        self.curr_state = WaitStage(self._loop, self._audio_service, self._stage, self._boxes,
                                    self.start_state_play_song, self.start_state_game_on)
        self._stage.set_stage_show_reading(True)
        self._stage.do_conffeti()
        chipped_boxes = []
        for player in self.players_service.registered_players.values():
            chipped_boxes.append(player.box_index)
        for box in self._boxes.get_alive():
            if box not in chipped_boxes:
                self._boxes.send_command_to_leds(box, None)

    def start_state_game_on(self):
        logging.info("start state 'game on`")
        self._boxes.shutdown_all_leds()
        self.cancel_prev_state()
        self.curr_state = Game(self._loop, self._audio_service, self._boxes, self.players_service, self._stage,
                               self.start_state_play_song)

