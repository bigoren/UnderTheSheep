import logging
from controllers.controller import Controller


class Song(Controller):

    song_list = ("useit.wav", "millenium.wav", "nocturne.wav", "essoteric.wav", "outlier.wav", "fever.wav", "lost.wav")

    def __init__(self, loop, audio_service, song_end_cb):
        super(Song, self).__init__()

        self._loop = loop
        self._audio_service = audio_service
        self._song_end_cb = song_end_cb
        self.curr_song_index = 0
        self._is_playing = False

    def choose_song(self):
        self._audio_service.stop_song()
        self._is_playing = False
        self._loop.call_later(2, self._do_play_song)

    def _do_play_song(self):
        selected_song = self.song_list[self.curr_song_index]
        logging.info("playing song index {0} named {1}".format(self.curr_song_index, selected_song))
        self._audio_service.play_song_request(selected_song)
        self._is_playing = True

    def song_end_event(self):
        if not self._is_playing:
            return

        self.curr_song_index = self.curr_song_index + 1
        if self.curr_song_index == len(self.song_list):
            self.curr_song_index = 0
        self._loop.call_soon(self._song_end_cb)

    def boxes_chip_event(self, msg_data, box_index):
        #nothing to do here, or maybe not?
        pass

    def stage_full_event(self, is_full):
        pass
