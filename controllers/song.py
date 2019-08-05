
from controllers.controller import Controller


class Song(Controller):

    song_list = ("alterego.wav", "millenium.wav", "nocturne.wav", "hound.wav", "essoteric.wav", "outlier")

    def __init__(self, loop, audio_service, song_end_cb):
        super(Song, self).__init__()

        self._loop = loop
        self._audio_service = audio_service
        self._song_end_cb = song_end_cb
        self.curr_song_index = 0

    def choose_song(self):
        selected_song = self.song_list[self.curr_song_index]
        print("playing song index {0} named {1}".format(self.curr_song_index, selected_song))
        self._audio_service.play_song_request(selected_song)
        self.curr_song_index = self.curr_song_index + 1
        if self.curr_song_index == len(self.song_list):
            self.curr_song_index = 0

    def _song_end_event(self):
        self._loop.call_soon(self._song_end_cb)