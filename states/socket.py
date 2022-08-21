from threading import Thread
import socketio
import eventlet
from states.base import BaseState


class Socket(Thread):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.players = {}
        self.sio = socketio.Server(cors_allowed_origins='*')
        self.app = socketio.WSGIApp(self.sio)
        self.register_events()

    def run(self):
        eventlet.wsgi.server(eventlet.listen(('', 5000)), self.app, log_output=False)

    def remove_player(self, sid):
        if sid not in self.players:
            return
        player = self.players[sid]
        player.on_leave()
        del self.players[sid]

    def register_events(self):
        @self.sio.event
        def join(sid, game):
            if sid in self.players:
                return
            game = self.main.get_game(game)
            if game is None:
                return

            player = game.player_class(self.sio, sid, game)
            self.players[sid] = player
            game.add_player(player)

        @self.sio.event
        def leave(sid):
            self.remove_player(sid)

        @self.sio.event
        def disconnect(sid):
            self.remove_player(sid)

        @self.sio.event
        def color(sid, new):
            if sid not in self.players:
                return
            self.players[sid].on_color(new)

        @self.sio.event
        def key_down(sid, key):
            if sid not in self.players:
                return
            self.players[sid].on_press(key)

        @self.sio.event
        def key_up(sid, key):
            if sid not in self.players:
                return
            self.players[sid].on_release(key)


class BasePlayer:
    def __init__(self, sio: socketio.Server, sid: str, game: BaseState):
        self.sio = sio
        self.sid = sid
        self.game = game

    def on_press(self, key):
        return

    def on_release(self, key):
        return

    def on_color(self, code):
        return

    def on_leave(self):
        return

    def set_color(self, code):
        self.sio.emit("color", code, room=self.sid)
