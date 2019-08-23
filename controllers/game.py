import logging
import random

from controllers.controller import Controller


class Game(Controller):

    yam_audio_list = ("/game_audio/yam.wav", "/game_audio/yam1.wav", "/game_audio/yam2.wav", "/game_audio/yam3.wav", "/game_audio/yam4.wav", "/game_audio/yam5.wav")
    land_audio_list = ("/game_audio/land.wav", "/game_audio/land1.wav", "/game_audio/land2.wav", "/game_audio/land3.wav", "/game_audio/land4.wav", "/game_audio/land5.wav")
    win_audio_list = ("/game_audio/win.wav", "/game_audio/win1.wav", "/game_audio/win2.wav", "/game_audio/win3.wav")
    lose_audio = "/game_audio/lose.wav"
    yam_and_land_list = yam_audio_list + land_audio_list
    max_rounds = 15

    def __init__(self, loop, audio_service, boxes_service, players_service, stage_service, game_end_cb):
        super(Game, self).__init__()

        self._loop = loop
        self._audio_service = audio_service
        self._boxes_service = boxes_service
        self._players_service = players_service
        self._stage_service = stage_service
        self._game_end_cb = game_end_cb
        # self._audio_service.register_on_song_end_event(self._song_end_event)
        self._prev_played_index = 0
        self._rounds = 0
        self._timeout_handle = None
        self._song_end = False
        self._was_full = False
        self._game_win = False
        self._game_lose = False
        self._game_over = False
        self._waiting_for_next_win = False
        self.choose_land_or_yam()

    def is_yam(self, index):
        return index < len(self.yam_audio_list)

    def is_land(self, index):
        return not self.is_yam(index)

    def choose_land_or_yam(self):
        if self._rounds == self.max_rounds:
            self._game_win = True
            self._stage_service.send_command_to_leds(animation_mode=4, fill_percent=0)
            self._stage_service.set_stage_show_reading(False)
            self._audio_service.play_song_request(self.win_audio_list[0])
            return
        self._rounds += 1

        random_selection = random.randint(1, len(self.yam_and_land_list) - 2)
        next_play_index = (self._prev_played_index + random_selection) % (len(self.yam_and_land_list))
        self._prev_played_index = next_play_index
        audio_file_name = self.yam_and_land_list[next_play_index]

        self._song_end = False
        logging.info("playing file {0}, round: {1}".format(audio_file_name, self._rounds))
        self._audio_service.play_song_request(audio_file_name)

        if self._timeout_handle is not None:
            self._timeout_handle.cancel()

    def stage_full_event(self, is_full):
        if self._game_lose or self._game_win:
            return
        if self.is_yam(self._prev_played_index):
            return
        elif is_full:
            self.choose_land_or_yam()
            self._was_full = True
        elif not is_full and self._was_full and not self._game_win:
            logging.info("Went off stage...")
            self.game_lose()
            self._was_full = False
        else:
            self._was_full = False

    def boxes_chip_event(self, msg_data, box_index):
        if self.is_land(self._prev_played_index):
            return
        if self._stage_service.is_full:
            logging.info("Lost because you chipped when the stage was full")
            self.game_lose()
        if not self._song_end:
            return
        if self._game_lose or self._game_win:
            return

        chip_uid = msg_data["UID"]
        player = self._players_service.get_registered_player(chip_uid)
        if player is None:
            return

        if player.chipped_box:
            return
        else:
            player.player_chipped_box(box_index)
            self._boxes_service.send_command_to_leds(box_index, None)

        if self._players_service.has_all_players_chipped():
            self.choose_land_or_yam()
            self._players_service.reset_players_chipped_state()

    def game_lose(self):
        if not self._game_lose:
            print("game lose, play lose audio and flag it")  # only when the audio ends the game will be over
            self._audio_service.play_song_request(self.lose_audio)
            self._stage_service.send_command_to_leds(animation_mode=3, fill_percent=0, led_color=0)
            self._stage_service.set_stage_show_reading(False)
            self._game_lose = True
            self._timeout_handle.cancel()

    def game_end(self):
        print("game over, calling game over callback")
        self._players_service.clean_players()
        self._timeout_handle.cancel()
        self._loop.call_soon(self._game_end_cb)
        return

    def game_win(self):
        if self._game_over:
            self.game_end()
        else:
            logging.info("Game finished, now play random song")
            selected_win = random.randint(1, len(self.win_audio_list) - 1)
            self._audio_service.play_song_request(self.win_audio_list[selected_win])
            self._game_over = True

    def song_end_event(self):
        if self._timeout_handle is not None:
            self._timeout_handle.cancel()
        self._timeout_handle = self._loop.call_later(25, self.game_end)
        if self._game_win:
            self.game_win()
            return
        elif self._game_lose:
            self.game_end()
            return

        self._song_end = True
        if self.is_yam(self._prev_played_index):
            for player in self._players_service.registered_players.values():
                self._boxes_service.send_command_to_leds(player.box_index, player.color)

        if self.is_land(self._prev_played_index):
            if self._stage_service.is_full:
                self.stage_full_event(self._stage_service.is_full)
