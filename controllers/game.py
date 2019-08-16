import random

from controllers.controller import Controller


class Game(Controller):

    yam_audio_list = ("/game_audio/yam.wav", "/game_audio/yam1.wav", "/game_audio/yam2.wav", "/game_audio/yam3.wav", "/game_audio/yam4.wav", "/game_audio/yam5.wav")
    land_audio_list = ("/game_audio/land.wav", "/game_audio/land1.wav", "/game_audio/land2.wav", "/game_audio/land3.wav", "/game_audio/land4.wav", "/game_audio/land5.wav")
    win_audio_list = ("/game_audio/win.wav", "/game_audio/win1.wav", "/game_audio/win2.wav", "/game_audio/win3.wav")
    # call_players_audio = "/game_audio/call_players.wav"
    # call_stage_audio = "/game_audio/call_stage.wav"
    # call_again_audio = ("/game_audio/call_again.wav", "/game_audio/call_again2.wav")

    def __init__(self, loop, audio_service, boxes_service, players_service, stage_service, song_end_cb):
        super(Game, self).__init__()

        self._loop = loop
        self._audio_service = audio_service
        self._boxes_service = boxes_service
        self._players_service = players_service
        self._stage_service = stage_service
        self._song_end_cb = song_end_cb
        self._audio_service.register_on_song_end_event(self._song_end_event)
        self.prev_yam_played = 0
        self.prev_land_played = 0
        self.prev_win_played = 0


    def choose_land_or_yam(self):
        # need to randomly? select yam or land with a flag for yam or land
        yam_and_land_list = self.yam_audio_list + self.land_audio_list
        random_selection = random.randint(0, 12) # make it size_of list?
        selected_yam_or_land = yam_and_land_list[random_selection]
        while selected_yam_or_land == self.prev_yam_played or selected_yam_or_land == self.prev_land_played:
            random_selection = random.randint(0, 12)  # make it size_of list?
            selected_yam_or_land = yam_and_land_list[random_selection]

        if random_selection > 5:    # not good code
            self.prev_land_played = selected_yam_or_land
        else:
            self.prev_yam_played = selected_yam_or_land

        print("playing selected {0}".format(selected_yam_or_land))
        self._audio_service.play_song_request(selected_yam_or_land)

    def _song_end_event(self):
        # what needs to happen at song end?
        self._loop.call_soon(self._song_end_cb)