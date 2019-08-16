from controllers.controller import Controller


class WaitStage(Controller):

    seconds_for_giveup = 40
    seconds_for_recall = 20

    song_for_recall = "game_audio/call_again.wav"
    song_call_for_stage = "game_audio/call_stage.wav"

    def __init__(self, loop, audio_service, stage_service, giveup_cb, stage_full_cb):
        super(WaitStage, self).__init__()

        self._loop = loop
        self._audio_service = audio_service
        self._stage_service = stage_service
        self._stage_full_cb = stage_full_cb
        self._giveup_cb = giveup_cb

        if not stage_service.get_is_alive():
            print("not waiting for stage - no connected stage")
            self._loop.call_soon(self._giveup_cb)
            return

        if stage_service.get_is_full():
            print("not waiting for stage - stage is already full")
            self._loop.call_soon(self._stage_full_cb)
            return

        self._audio_service.play_song_request(self.song_call_for_stage)
        self.reg_handlers.append(self._loop.call_later(self.seconds_for_giveup, self._giveup_cb))
        self.reg_handlers.append(self._loop.call_later(self.seconds_for_recall, self._audio_service.play_song_request,
                                                       self.song_for_recall))

    def stage_full_event(self, is_full):
        if is_full:
            self._loop.call_soon(self._stage_full_cb)
