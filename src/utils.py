from functools import wraps
from datetime import datetime
from flask import flash, redirect, url_for, session


def get_utc_now():
    return datetime.utcnow()

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Vous devez être connecté pour accéder à cette page.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("user_id") is None or not session.get("role") == "admin":
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapped_view

