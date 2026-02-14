"""Modèle User pour les utilisateurs du site (admin, gérant, client)."""

from werkzeug.security import check_password_hash, generate_password_hash
from typing import Any, cast
from src.models.database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    tickets = db.relationship("Ticket", back_populates="author", lazy=True)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def find_by_id(cls, user_id: int) -> "User | None":
        """Retourne un utilisateur par son id ou None s'il n'existe pas."""
        return cast("User | None", cls.query.get(user_id))

    @classmethod
    def find_by_email(cls, email: str) -> "User | None":
        """Retourne un utilisateur par son email ou None s'il n'existe pas."""
        return cast("User | None", cls.query.filter_by(email=email).first())

    @classmethod
    def find_by_username(cls, username: str) -> "User | None":
        """Retourne un utilisateur par son username ou None s'il n'existe pas."""
        return cast("User | None", cls.query.filter_by(username=username).first())

    @classmethod
    def find_all(cls) -> list["User"]:
        """Retourne la liste de tous les utilisateurs."""
        return cast(list[User], cls.query.all())
    

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)


    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def is_admin_user(cls) -> bool:
        return cls.role == "admin"

    @classmethod
    def create_user(cls, username: str, email: str, password: str, role: str = "user") -> "User":
        """Crée un nouvel utilisateur et le retourne."""
        user = cls(username=username, email=email, password_hash = generate_password_hash(password) , role=role)
        db.session.add(user)
        db.session.commit()
        return user
