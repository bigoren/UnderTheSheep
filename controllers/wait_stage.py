import logging
import random

from controllers.controller import Controller


class WaitStage(Controller):

    seconds_for_giveup = 40
    seconds_for_recall = 20

    song_call_for_stage = "game_audio/call_stage.wav"
    song_for_recall = "game_audio/call_again.wav"
    song_ready_set_game_list = ("game_audio/ready_set_game.wav", "game_audio/ready_3_2_1.wav")

    def __init__(self, loop, audio_service, stage_service, boxes_service, giveup_cb, stage_full_cb):
        super(WaitStage, self).__init__()

        self._loop = loop
        self._audio_service = audio_service
        self._stage_service = stage_service
        self._boxes_service = boxes_service
        self._stage_full_cb = stage_full_cb
        self._giveup_cb = giveup_cb
        self._wait_stage_end = False
        self._stage_full_finished = False
        self._should_play = False

        if not stage_service.get_is_alive():
            logging.info("not waiting for stage - no connected stage")
            self._loop.call_soon(self._giveup_cb)
            return

        if stage_service.get_is_full():
            logging.info("not waiting for stage - stage is already full")
            self._loop.call_soon(self._stage_full_cb)
            return

        self._audio_service.play_song_request(self.song_call_for_stage)
        self.reg_handlers.append(self._loop.call_later(self.seconds_for_giveup, self._giveup_cb))
        self.reg_handlers.append(self._loop.call_later(self.seconds_for_recall, self._audio_service.play_song_request,
                                                       self.song_for_recall))

    def stage_full_event(self, is_full):
        if is_full:
            self._wait_stage_end = True
            sel_ready_idx = random.randint(0, 1)
            self._stage_service.set_stage_show_reading(False)
            self._stage_service.send_command_to_leds(animation_mode=3, fill_percent=1)
            self.cancel_timers()
            if self._should_play:
                logging.info("Playing in full event")
                self._audio_service.play_song_request(self.song_ready_set_game_list[sel_ready_idx])
                self._should_play = False
                self._stage_full_finished = True
            else:
                self._audio_service.stop_song()

    def song_end_event(self):
        if not self._wait_stage_end:
            self._should_play = True

        if self._wait_stage_end and not self._stage_full_finished:
            sel_ready_idx = random.randint(0, 1)
            logging.info("Playing in song end")
            self._audio_service.play_song_request(self.song_ready_set_game_list[sel_ready_idx])
            self._boxes_service.shutdown_all_leds()
            self._stage_full_finished = True
        elif self._stage_full_finished:
            self._stage_service.set_stage_show_reading(True)
            self._stage_service.send_command_to_leds(animation_mode=0, fill_percent=0)
            self._loop.call_soon(self._stage_full_cb)
