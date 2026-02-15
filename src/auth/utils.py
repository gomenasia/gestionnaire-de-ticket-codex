from typing import Optional
from flask import session
from src.models import User

def get_current_user() -> Optional["User"]:
    return getattr(g, 'user', None)