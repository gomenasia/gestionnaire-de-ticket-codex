from flask import Blueprint, g
from flask_socketio import emit, join_room
from src.models.database import db
from src.models.message import Message
from src.models.channel import Channel
from src.models.ticket import Ticket
from app import socketio

chat_bp = Blueprint("chat", __name__)

@socketio.on("join")
def on_join(data):
    channel_id = data["channel_id"]
    join_room(f"channel_{channel_id}")

@socketio.on("send_message")
def on_message(data):
    channel_id = data["channel_id"]
    content    = data["content"].strip()

    if not content:
        return

    msg = Message(
        content    = content,
        author_id  = g.id,
        channel_id = channel_id
    )
    db.session.add(msg)
    db.session.commit()

    emit("new_message", {
        "id":       msg.id,
        "content":  msg.content,
        "author":   g.username,
        "channel_id": channel_id
    }, to=f"channel_{channel_id}")