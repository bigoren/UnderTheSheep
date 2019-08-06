import asyncio
import json

from aiohttp import ClientSession


class AudioService:

    player_host = "10.0.0.200"

    def __init__(self, loop, mqtt_client):
        self.mqtt_client = mqtt_client
        self._loop = loop
        self._on_song_end_event = None

    def mqtt_sub(self):
        self.mqtt_client.subscribe("current-song", 1)
        self.mqtt_client.message_callback_add("current-song", self._on_message_player)

    def play_song_request(self, file_name):
        self._loop.create_task(self._play_song_request_async(file_name))

    def _on_message_player(self, client, userdata, message):
        print("Player Message Received: " + message.payload.decode())
        payload = json.loads(message.payload)
        if not payload["song_is_playing"]:
            self.call_song_end_event()

    async def _play_song_request_async(self, file_name):
        try:
            async with ClientSession() as session:
                player_msg = {'file_id': file_name, 'start_offset_ms': 0}
                url = "http://{0}:8080/api/current-song".format(self.player_host)
                r = await self._player_request(url, session, player_msg)
                return r
        except:
            print("error playing song {}".format(file_name))

    async def _player_request(self, url: str, session: ClientSession, player_msg):
        """POST request wrapper to send a json over http."""
        async with await session.put(url=url, json=player_msg) as resp:
            resp.raise_for_status()
            #logger.info("Got response [%s] for POST to player url: %s", resp.status, url)
            return resp

    def register_on_song_end_event(self, func):
        self._on_song_end_event = func
        self.call_song_end_event()

    def call_song_end_event(self):
        if self._on_song_end_event is not None:
            self._loop.call_soon(self._on_song_end_event)
