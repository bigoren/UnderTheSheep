import random

from controllers.controller import Controller


class Game(Controller):

    yam_audio_list = ("/game_audio/yam.wav", "/game_audio/yam1.wav", "/game_audio/yam2.wav", "/game_audio/yam3.wav", "/game_audio/yam4.wav", "/game_audio/yam5.wav")
    land_audio_list = ("/game_audio/land.wav", "/game_audio/land1.wav", "/game_audio/land2.wav", "/game_audio/land3.wav", "/game_audio/land4.wav", "/game_audio/land5.wav")
    win_audio_list = ("/game_audio/win.wav", "/game_audio/win1.wav", "/game_audio/win2.wav", "/game_audio/win3.wav")
    yam_and_land_list = yam_audio_list + land_audio_list
    # call_players_audio = "/game_audio/call_players.wav"
    # call_stage_audio = "/game_audio/call_stage.wav"
    # call_again_audio = ("/game_audio/call_again.wav", "/game_audio/call_again2.wav")

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

    def is_yam(self, index):
        return index < len(self.yam_audio_list)

    def is_land(self, index):
        return not self.is_yam(index)

    def choose_land_or_yam(self):
        if self._rounds == self.max_rounds:
            self.game_end()
            return

        random_selection = random.randint(1, len(self.yam_and_land_list))
        next_play_index = (self._prev_played_index + random_selection) % len(self.yam_and_land_list)
        self._prev_played_index = next_play_index
        audio_file_name = self.yam_and_land_list[next_play_index]

        self._rounds += 1

        print("playing file {0}, round: {1}".format(audio_file_name, self._rounds))
        self._audio_service.play_song_request(audio_file_name)

        self._loop.call_later(10, self._yam_land_timedout)

    def _yam_land_timedout(self):
        self.choose_land_or_yam()

    # def _song_end_event(self):
        # what needs to happen at song end?
        # self._loop.call_soon(self._song_end_cb)

    def stage_full_event(self, is_full):
        pass

    def game_end(self):
        print("game over, calling game over callback")
        self._loop.call_soon(self._game_end_cb)
        return
