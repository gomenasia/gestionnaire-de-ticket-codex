"""Modèle message pour les conversation"""

from datetime import date
from typing import cast
from src.models.database import db
from src.utils import get_utc_now


class Channel(db.Model):
    "Modèle representant une discution"

    __tablename__ = "channel"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default = get_utc_now(), nullable=True)

    # Relation parent-enfant
    ticket = db.relationship('Ticket', back_populates="channel")
    messages = db.relationship("Message", back_populates="channel")

    # INCOMPLETE

    def __repr__(self) -> str:
        return f"<Channel {self.name} (created_at: {self.create_at}), associated ticket {self.ticket.id}>"

    @classmethod
    def find_by_id(cls, channel_id: int) -> "Channel | None":
        """Retourne un channel par son id ou None s'il n'existe pas."""
        return cast("Channel | None", cls.query.get(channel_id))
    
    @classmethod
    def find_all(cls) -> list["Channel"]:
        """Retourne la liste de tous les tickets."""
        return cast(list[Channel], cls.query.all())
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at
        }
    
    @classmethod
    def create(cls, **kwargs) -> "Channel":
        ticket = cls(**kwargs)
        db.session.add(ticket)
        db.session.commit()
        return ticket 