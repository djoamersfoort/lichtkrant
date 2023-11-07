from abc import abstractmethod
from typing import Dict
from enum import Enum

import socketio
from hypercorn.asyncio import serve
from hypercorn.config import Config

from states.base import BaseState


class ClientState(Enum):
    def __str__(self):
        return str(self.value)

    MENU = 'menu'
    READYING = 'readying'
    PLAYING = 'playing'


class Socket:
    def __init__(self, main, port: int):
        super().__init__()
        self.main = main
        self.players: Dict[str, BasePlayer] = {}
        self.sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
        self.app = socketio.ASGIApp(self.sio, static_files={
            '/': './static/lichtkrant-client/index.html',
            '': './static/lichtkrant-client'
        })
        self.port = port

        self.register_events()

    async def start(self):
        config = Config()
        config.bind = f"0.0.0.0:{self.port}"

        return await serve(self.app, config)

    def remove_player(self, sid: str):
        if sid not in self.players:
            return
        player = self.players[sid]
        player.on_leave()
        del self.players[sid]

    def register_events(self):
        @self.sio.event()
        async def connect(sid: str, _environ, _auth):
            await self.sio.emit("games", self.main.games, room=sid)

        @self.sio.event
        async def join(sid: str, game: str):
            if sid in self.players:
                return
            game: BaseState = self.main.get_game(game)
            if game is None:
                return

            player: BasePlayer = game.player_class(self.sio, sid, game)
            self.players[sid] = player

            response = await game.add_player(player)
            if not response:
                await player.set_state(ClientState.PLAYING)
            else:
                await player.set_state(response)

        @self.sio.event
        async def leave(sid: str):
            self.remove_player(sid)

        @self.sio.event
        async def disconnect(sid: str):
            self.remove_player(sid)

        @self.sio.event
        async def ready_state(sid: str, state: bool):
            self.players[sid].on_ready_change(state)

        @self.sio.event
        async def color(sid: str, new: str):
            if sid not in self.players:
                return
            self.players[sid].on_color(new)

        @self.sio.event
        async def key_down(sid: str, key: str):
            if sid not in self.players:
                return
            self.players[sid].on_press(key)

        @self.sio.event
        async def key_up(sid: str, key: str):
            if sid not in self.players:
                return
            self.players[sid].on_release(key)


class BasePlayer:
    def __init__(self, sio: socketio.Server, sid: str, game: BaseState):
        self.sio = sio
        self.sid = sid
        self.game = game

    @abstractmethod
    def on_press(self, key: str):
        return

    def on_release(self, _key: str):
        return

    def on_color(self, _code: str):
        return

    def on_ready_change(self, _state: bool):
        return

    def on_leave(self):
        return

    async def set_color(self, code: str):
        await self.sio.emit("color", code, room=self.sid)

    async def set_state(self, state: ClientState):
        await self.sio.emit("state", str(state), self.sid)
