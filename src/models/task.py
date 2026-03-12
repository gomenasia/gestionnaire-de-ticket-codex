"""ModÃ¨le Task pour les taches du planning."""

from typing import Any, cast, Optional
from src.models.database import db


class Task(db.Model):
    "ModÃ¨le Task reprÃ©snetant les tahce d'un Plannning"

    __tablename__ = "Task"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    assign_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=True)

    # Relation parent-enfant
    parent_id = db.Column(db.Integer, db.ForeignKey('Task.id'), nullable=True)
    parent = db.relationship('Task', remote_side=[id], backref='subtasks')
    author = db.relationship(
        "User", 
        foreign_keys=[author_id],
        back_populates="task"
    )
    assign = db.relationship(
        "User", 
        foreign_keys=[assign_id],
        back_populates="work"
    )

    def __repr__(self) -> str:
        return f"<Task {self.title} (status:{self.status})>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "status": self.status,
            "author": self.author_id,
            "assigned": self.assign_id, 
            "parent_id": self.parent_id,
            "parent_title": self.parent.title if self.parent else None,
            "subtasks": [s.to_dict() for s in self.subtasks] if self.subtasks else []
        }

    @classmethod
    def create_Task(cls, title: str, content: str, user_id: int, assigned_id: int=None, parent_id : int=None) -> "Task":
        task = cls(title=title, content=content, status=False, author_id=user_id, assign_id=assigned_id, parent_id=parent_id)
        db.session.add(task)
        db.session.flush()
        db.session.commit()
        return task
    
    def delete_Task(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def update_status(self, status_up: bool) -> None:
        if hasattr(self, "status"):
            setattr(self, "status", status_up)
        db.session.add(self)
        db.session.commit()
    
    def update_assign(self, assign_id: int) -> None:
        if hasattr(self, "assign_id"):
            setattr(self, "assign_id", assign_id)
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all(cls) -> list["Task"]:
        """Retourne la liste de toutes les Task"""
        return cast(list["Task"], cls.query.filter_by(parent_id=None).all())
    
    @classmethod
    def find_by_id(cls, task_id: int) -> Optional["Task"]:
        """Retourne les tâches créées par un user"""
        return cast(Optional["Task"], cls.query.filter_by(id=task_id).first())

    @classmethod
    def find_by_author(cls, user_id: int) -> Optional[list["Task"]]:
        """Retourne les tâches créées par un user"""
        return cast(Optional[list["Task"]], cls.query.filter_by(author_id=user_id).all())

    @classmethod
    def find_by_title(cls, title: str) -> Optional["Task"]:
        """Retourne une tâche par son titre."""
        return cast(Optional["Task"], cls.query.filter_by(title=title).first())
    
    @classmethod
    def find_subtasks_by_parent_id(cls, parent_id: int) -> list["Task"]:
        """Retourne toutes les sous-tÃ¢ches d'une tÃ¢che par son ID."""
        return cast(list["Task"], cls.query.filter_by(parent_id=parent_id).all())
    
    @classmethod
    def find_parent_by_parent_id(cls, parent_id:int) -> Optional["Task"]:
        return cast(Optional["Task"], cls.query.filter_by(id=parent_id).first())


    @property
    def completion_count(self) -> int:
        subtasks = self.find_subtasks_by_parent_id(self.id)
        if not subtasks:
            return (1 if self.status else 0,1)
        completed = sum(1 for s in subtasks if s.status)
        return (completed, len(subtasks))
    
    @property
    def completion_rate(self) -> float:
        subtasks = self.find_subtasks_by_parent_id(self.id)
        if not subtasks:
            if self.status == 1:
                return 100.0
            else:
                return 0.0
        completed = sum(1 for s in subtasks if s.status)
        return ((completed / len(subtasks))*100)

