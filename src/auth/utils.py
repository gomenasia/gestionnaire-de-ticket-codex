from typing import Optional
from flask import session
from src.models import User

def get_current_user() -> Optional["User"]:
    id = session.get("user_id")
    if id:
        user = User.find_by_id(id)
        if user:
            return user
        return None
    return None