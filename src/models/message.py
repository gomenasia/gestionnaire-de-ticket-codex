"""Modèle message pour les conversation"""

from src.utils import get_utc_now
from typing import cast
from src.models.database import db


class Message(db.Model):
    "Modèle representant les message lier a une discution"

    __tablename__ = "Message"

    id         = db.Column(db.Integer, primary_key=True)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=get_utc_now())

    # Clés étrangères
    author_id  = db.Column(db.Integer, db.ForeignKey("user.id"),    nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey("channel.id"), nullable=False)

    # Relations
    author  = db.relationship("User",    back_populates="messages")
    channel = db.relationship("Channel", back_populates="messages")

    @classmethod
    def find_by_id(cls, message_id: int) -> "Message | None":
        """Retourne un message par son id ou None s'il n'existe pas."""
        return cast("Message | None", cls.query.get(message_id))
    
    @classmethod
    def find_by_channel_id(cls, channel_id: int) -> list["Message"]:
        """Retourne un channel par son id ou None s'il n'existe pas."""
        return cast(list[Message], cls.query.filter(Message.channel_id == channel_id).all())

    @classmethod
    def find_since(cls, channel_id: int, since: int) -> list["Message"]:
        """Retourne les message d'un channel depuis since."""
        return cast(list[Message], cls.query.filter(Message.channel_id == channel_id, Message.id > since).all())
    
    @classmethod
    def find_all(cls) -> list["Message"]:
        """Retourne la liste de tous les tickets."""
        return cast(list[Message], cls.query.all())
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at,
            "author_id": self.author_id,
            "channel_id": self.channel_id
        }
    
    @classmethod
    def create(cls, **kwargs) -> "Message":
        ticket = cls(**kwargs)
        db.session.add(ticket)
        db.session.commit()
        return ticket 