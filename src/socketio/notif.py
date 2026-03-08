from flask_socketio import join_room

from flask import g
from app import socketio

@socketio.on("connect")
def on_connect():
    if hasattr(g, "user"):
        join_room(f"user_{g.user.id}")

@socketio.on("disconnect")
def on_disconnect():
    pass  # Flask-SocketIO gère la sortie automatiquement