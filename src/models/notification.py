"""Modèle message pour les notification"""

from typing import cast
from src.utils import get_utc_now
from src.models.database import db

class Notification(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message     = db.Column(db.String(255), nullable=False)
    type        = db.Column(db.String(50))        # ex: "statut", "reponse", "deadline"
    ticket_id   = db.Column(db.Integer, db.ForeignKey("ticket.id"))
    is_read     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=get_utc_now())

    user   = db.relationship("User", backref="notifications")
    ticket = db.relationship("Ticket", backref="notifications")

    @classmethod
    def find_by_user(cls, user_id: int) -> list["Notification"]:
        """Retourne les notif destiner a un user"""
        return cast(list["Notification"], cls.query.filter_by(user_id=user_id).all())


    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "type": self.type,
            "is_read": self.is_read,
            "ticket_id": self.ticket_id,
            "created_at": self.created_at
        }
    
    @classmethod
    def create(cls, **kwargs) -> "Notification":
        notification = cls(**kwargs)
        db.session.add(notification)
        db.session.commit()
        return notification 

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)
        self.updated_at = get_utc_now()
        self.save()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()