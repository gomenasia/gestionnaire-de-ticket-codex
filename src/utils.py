from functools import wraps
from datetime import datetime, timezone
from flask import flash, g, redirect, url_for


def get_utc_now():
    return datetime.now(timezone.utc)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not hasattr(g, "user") or g.user is None:
            # Pour les routes API, on retourne une erreur JSON
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Authentification requise", "message":"Vous devez être connecté pour faire cette action."}), 401
            flash("Vous devez être connecté pour accéder à cette page.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not hasattr(g, "user") or g.user is None or not g.user.is_admin_user():
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapped_view

