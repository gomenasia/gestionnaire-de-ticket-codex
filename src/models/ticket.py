"""Modèle Ticket pour les tickets du système de gestion."""

from src.models.database import db
from src.utils import get_utc_now
from typing import cast


class Ticket(db.Model):
    """
    Modèle Ticket représentant un ticket de support.
    """

    __tablename__ = "Ticket"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="en_attente", nullable=False)
    categorie = db.Column(db.String(20), default="question", nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: get_utc_now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: get_utc_now(), nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    author = db.relationship("User", back_populates="tickets")

    channel_id = db.Column(db.Integer, db.ForeignKey("Channel.id"), nullable=True)

    channel = db.relationship("Channel", back_populates="ticket")

    def __repr__(self) -> str:
        return f"<Ticket {self.title} (status: {self.status})>"

    @classmethod
    def find_by_id(cls, ticket_id: int) -> "Ticket | None":
        """Retourne un ticket par son id ou None s'il n'existe pas."""
        return cast("Ticket | None", cls.query.get(ticket_id))
    
    @classmethod
    def find_all(cls) -> list["Ticket"]:
        """Retourne la liste de tous les tickets."""
        return cast(list[Ticket], cls.query.all())

    @classmethod
    def find_all_by_user(cls, user_id: int) -> list["Ticket"]:
        """Retourne la liste de tous les tickets."""
        return cast(list[Ticket], cls.query.filter_by(author_id=user_id).order_by(Ticket.created_at.desc()).all())
    
    @classmethod
    def find_all_by_status(cls, targeted_status: str) -> list["Ticket"]:
        """Retourne la liste de tous les tickets du statuss specifier."""
        return cast(list[Ticket], cls.query.filter_by(status = targeted_status).order_by(Ticket.created_at.desc()).all())
    
    @classmethod
    def find_all_by_categorie(cls, targeted_categorie: str) -> list["Ticket"]:
        """Retourne la liste de tous les tickets de la categorie specifier."""
        return cast(list[Ticket], cls.query.filter_by(categorie = targeted_categorie).order_by(Ticket.created_at.desc()).all())
    
    @classmethod
    def find_by_channel_id(cls, channel_id: int) -> "Ticket | None":
        """renoie le ticket lier au channel si il exist"""
        return cast("Ticket | None", cls.query.filter_by(channel_id= channel_id))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "categorie": self.categorie,
            "status": self.status,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author_id": self.author_id,
        }
    
    @classmethod
    def create(cls, **kwargs) -> "Ticket":
        ticket = cls(**kwargs)
        db.session.add(ticket)
        db.session.commit()
        return ticket 

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)
        self.updated_at = get_utc_now()
        self.save()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()