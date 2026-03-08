from flask_socketio import emit, join_room

from flask import  session
from app import socketio
from src.models import User
from src.models.message import Message

@socketio.on("join")
def on_join(data):
    channel_id = data.get("channel_id")
    if channel_id is None:
        return

    join_room(f"channel_{int(channel_id)}")


@socketio.on("send_message")
def on_message(data):
    user_id = session.get("user_id")
    if user_id is None:
        emit("error_message", {"message": "Vous devez être connecté pour envoyer un message."})
        return

    user = User.find_by_id(user_id)
    if user is None:
        emit("error_message", {"message": "Utilisateur introuvable."})
        return

    channel_id = data.get("channel_id")
    content = data.get("content", "").strip()

    if channel_id is None or not content:
        return
    


    msg = Message.create(content=content, author_id=user.id, channel_id=int(channel_id))

    emit(
        "new_message",
        {
            "id": msg.id,
            "content": msg.content,
            "author": user.username,
            "author_id": user.id,
            "channel_id": int(channel_id),
        },
        to=f"channel_{int(channel_id)}",
    )