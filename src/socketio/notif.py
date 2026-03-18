"""gere les room socketio pour les notification"""

from flask_socketio import join_room
from flask import session
from src.extensions import socketio

@socketio.on("connect")
def on_connect():
    user_id = session.get("user_id")
    print(f"[SocketIO] connect → user_id={user_id}") #TODO remove me
    if user_id:
        join_room(f"user_{user_id}")
        print(f"[SocketIO] joined room user_{user_id}")  #TODO remove me

@socketio.on("disconnect")
def on_disconnect():
    pass  # Flask-SocketIO gère la sortie automatiquement
