from typing import Optional

from flask import g, session

from src.models import User


def load_logged_in_user() -> None:
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
        return

    g.user = User.find_by_id(user_id)


def get_current_user() -> Optional["User"]:
    return getattr(g, "user", None)
