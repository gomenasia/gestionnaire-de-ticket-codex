"""crer la connection socketio"""

from flask_socketio import SocketIO

socketio = SocketIO(async_mode='gevent', cors_allowed_origins="*")
