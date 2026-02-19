"""ModÃ¨le Task pour les taches du planning."""

from datetime import date
from typing import Any, cast

from src.models.database import db


class Task(db.Model):
    "ModÃ¨le Task reprÃ©snetant les tahce d'un Plannning"

    __tablename__ = "Task"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Relation parent-enfant
    parent_id = db.Column(db.Integer, db.ForeignKey('Task.id'), nullable=True)
    parent = db.relationship('Task', remote_side=[id], backref='subtasks')
    author = db.relationship("User", back_populates="task")

    def __repr__(self) -> str:
        return f"<Task {self.title} (status:{self.status})>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "status": self.status,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "author": self.author_id,
            "parent_id": self.parent_id,
            "parent_title": self.parent.title if self.parent else None,
            "subtasks": [s.to_dict() for s in self.subtasks] if self.subtasks else [],
        }

    @classmethod
    def create_Task(cls, title: str, content: str, deadline: date, user_id: int, parent_id:int=None) -> "Task":
        task = cls(title=title, content=content, status=False, 
                deadline=deadline, author_id=user_id, parent_id=parent_id)
        db.session.add(task)
        db.session.commit()
        return task

    def update_status(self, status_up: bool) -> None:
        if hasattr(self, "status"):
            setattr(self, "status", status_up)
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all(cls) -> list["Task"]:
        """Retourne la liste de toutes les Task"""
        return cast(list["Task"], cls.query.all())

    @classmethod
    def find_by_author(cls, user_id: int) -> list["Task"] | None:
        """Retourne les tache crÃ©e par un user"""
        return cast(list["Task"] | None, cls.query.filter_by(author_id= user_id).all())

    @classmethod
    def find_by_title(cls, title: str) -> "Task | None":
        """Retourne une tÃ¢che par son titre."""
        return cast("Task | None", cls.query.filter_by(title=title).first())
    
    @classmethod
    def find_subtasks_by_parent_id(cls, parent_id: int) -> list["Task"]:
        """Retourne toutes les sous-tÃ¢ches d'une tÃ¢che par son ID."""
        return cast(list["Task"], cls.query.filter_by(parent_id=parent_id).all())

