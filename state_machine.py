import asyncio

from aiohttp import ClientSession


class UnderTheSeaState:
    play_song = "playing_song"
    wait_for_players = "wait_for_players"
    wait_for_stage = "wait_for_stage"
    game_on = "game_on"

    def __init__(self, stage):
        self.curr_state = self.play_song
        self.state_handlers = []
        self._stage = stage

    def song_ended(self):
        if self.curr_state == self.play_song:
            self.start_state_wait_for_players()

    def start_state_play_song(self):
        self.change_state(self.play_song)
        asyncio.create_task(self.play_song_request("alterego.wav"))

    def start_state_wait_for_players(self):
        self.change_state(self.wait_for_players)
        asyncio.create_task(self.play_song_request("call_for_players.wav"))
        self.state_handlers.append(self._loop.call_later(15, self.start_state_play_song))
        self.state_handlers.append(self._loop.call_later(5, self.play_song_request, "call_again.wav"))

    def start_state_wait_for_stage(self):
        self.change_state(self.wait_for_stage)
        asyncio.create_task(self.play_song_request("call_for_stage.wav"))
        self.state_handlers.append(self._loop.call_later(30, self.start_state_play_song))
        self.state_handlers.append(self._loop.call_later(15, self.play_song_request, "call_again_for_stage.wav"))
        self._stage.register_on_full(self.start_state_game_on)

    def start_state_game_on(self):
        self.change_state(self.game_on)

    def change_state(self, new_state):
        for handler in self.state_handlers:
            handler.cancel()
        self.state_handlers = []
        self.curr_state = new_state

    def on_all_chips_received(self):
        self._loop.call_soon(self.start_state_wait_for_stage)
        self.change_state(self.wait_for_stage)

    async def play_song_request(self, file_name):
        try:
            async with ClientSession() as session:
                player_msg = {'file_id': file_name, 'start_offset_ms': 0}
                r = await self.player_request("http://10.0.0.200:8080/api/current-song", session, player_msg)
                return r
        except:
            print("error playing song {}".format(file_name))

    async def player_request(self, url: str, session: ClientSession, player_msg):
        """POST request wrapper to send a json over http."""
        async with await session.put(url=url, json=player_msg) as resp:
            resp.raise_for_status()
            #logger.info("Got response [%s] for POST to player url: %s", resp.status, url)
            return resp
