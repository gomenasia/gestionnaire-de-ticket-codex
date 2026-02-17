"""Modèle Task pour les taches du planning."""

from src.models.database import db


class Task(db.Model):
    "Modèle Task représnetant les tahce d'un Plannning"

    __tablename__ = "Task"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", back_populates="task")

    def __repr__(self) -> str:
        return f"<Task{self.title} (status:{self.status})"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            
        }