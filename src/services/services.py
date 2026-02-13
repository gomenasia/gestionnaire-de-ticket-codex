from functools import wraps
from flask import flash, g, redirect, url_for
from datetime import datetime


def get_utc_now():
    return datetime.utcnow()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Vous devez être connecté pour accéder à cette page.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None or not g.user.is_admin:
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapped_view