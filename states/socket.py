from threading import Thread
import socketio
import eventlet


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
        self.players[sid].remove()
        del self.players[sid]

    def register_events(self):
        @self.sio.event
        def join(sid, game):
            if sid in self.players:
                return
            player = Player(self.sio, sid)
            self.players[sid] = player
            self.main.add_player(game, player)

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
            self.players[sid].color(new)

        @self.sio.event
        def key_down(sid, key):
            if sid not in self.players:
                return
            self.players[sid].key_down(key)

        @self.sio.event
        def key_up(sid, key):
            if sid not in self.players:
                return
            self.players[sid].key_up(key)


class Player:
    def __init__(self, sio, sid):
        self.sio = sio
        self.sid = sid
        self.pressListeners = []
        self.releaseListeners = []
        self.leaveListeners = []
        self.colorListeners = []
        self.data = {}

    def on_press(self, listener):
        self.pressListeners.append(listener)

    def on_release(self, listener):
        self.releaseListeners.append(listener)

    def on_leave(self, listener):
        self.leaveListeners.append(listener)

    def on_color(self, listener):
        self.colorListeners.append(listener)

    def set_color(self, code):
        self.sio.emit("color", code, room=self.sid)

    def get_flag(self, flag):
        return flag in self.data and self.data[flag]

    def key_down(self, key):
        for listener in self.pressListeners:
            if self.get_flag("use_player_in_key"):
                listener(self, key)
            else:
                listener(key)

    def key_up(self, key):
        for listener in self.releaseListeners:
            if self.get_flag("use_player_in_key"):
                listener(self, key)
            else:
                listener(key)

    def color(self, new):
        if len(new) == 7 and new.startswith("#"):
            for listener in self.colorListeners:
                if self.get_flag("use_player_in_color"):
                    listener(self, new)
                else:
                    listener(new)

    def remove(self):
        for listener in self.leaveListeners:
            if self.get_flag("use_player_in_leave"):
                listener(self)
            else:
                listener()
