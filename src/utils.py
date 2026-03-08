from functools import wraps
from datetime import datetime, timezone
from flask import flash, g, redirect, url_for, request, jsonify
from functools import wraps
from app import socketio
from sqlalchemy.exc import OperationalError, DatabaseError

def handle_db_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except OperationalError:
            return jsonify({"error": "Database unavailable"}), 503
        except DatabaseError as e:
            return jsonify({"error": "Database error", "detail": str(e)}), 500
    return wrapper

def get_utc_now():
    return datetime.now(timezone.utc)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not hasattr(g, "user") or g.user is None:
            # Pour les routes API, on retourne une erreur JSON
            if request.is_json or request.path.startswith("/tasks/"):
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

def send_notification(user_id: int, message: str, notification_type: str, ticket_id: int =None):
    notif = url_for("api.create_notif",
                    user_id=user_id,
                    message=message,
                    notification_type=notification_type,
                    ticket_id=ticket_id)
    

    # Envoyer en temps réel via WebSocket
    socketio.emit(
        "new_notification",
        {
            "message": message,
            "notification_type": notification_type,
            "ticket_id": ticket_id
        },
        room=f"user_{user_id}"   # room privée par utilisateur
    )
