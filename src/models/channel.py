"""Modèle message pour les conversation"""

from datetime import date
from typing import Any, cast
from typing import Optional, cast
from src.models.database import db


class Channel(db.Model):
    "Modèle representant une discution"

    __tablename__ = "channel"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relation parent-enfant
    ticket = db.relationship('Ticket', back_populates="channel")
    messages = db.relationship("Message", back_populates="channel")

    # INCOMPLETE