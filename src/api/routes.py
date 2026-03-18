"""API pour l'application."""

from flask import jsonify, request, session
from src.models import Ticket, Notification, Task, Message
from src.utils import handle_db_errors, login_required
from . import api_bp


@api_bp.route("/tickets")
@handle_db_errors
def get_ticket():
    """API pour récupérer les tickets filtrés en JSON."""

    tickets = Ticket.find_all()
    return jsonify([ticket.to_dict() for ticket in tickets]), 200

@api_bp.route("/tasks")
@handle_db_errors
def get_task():
    """API pour récupérer les tache filtrés en JSON."""

    taches = Task.find_all()
    return jsonify([tache.to_dict() for tache in taches]), 200


@api_bp.route("/channel/<int:channel_id>/messages")
@handle_db_errors
def get_messages(channel_id):
    since = request.args.get("since", 0)
    messages = Message.find_since(channel_id, since)
    return jsonify([m.to_dict() for m in messages]), 200

@api_bp.route('/session')
def get_session():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            'success': False,
            'user_id': None,
            'username': None,
            'role': None
        }), 401

    return jsonify({
        'success': True,
        'user_id': user_id,
        'username': session.get('username'),
        'role': session.get('role')
    }), 200

    # ============================= NOTIFICATION =============================

@api_bp.route('/notification/<int:user_id>')
@handle_db_errors
@login_required
def get_notif_by_user(user_id):
    notifs = Notification.find_by_user(user_id)
    return jsonify([notification.to_dict() for notification in notifs]), 200

@api_bp.route('/notification/unread-counts', methods=['GET'])
@handle_db_errors
@login_required
def unread_notification_counts():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({}), 401

    count = Notification.get_notif_count_by_user(user_id)

    return jsonify({"count": count}), 200


@api_bp.route('/notification/mark-read', methods=['POST'])
def mark_notification_as_read():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Non authentifié'}), 401

    data = request.get_json()
    notif = Notification.find_by_id(data.get('notification_id'))

    updated = Notification.marke_read(notif)
    return jsonify({'updated': updated}), 200


    # ===================================== MESSAGE ==============================


# ── Nb de messages non lus par ticket (pour moi) ──────────
@api_bp.route('/messages/unread-counts', methods=['GET'])
@handle_db_errors
@login_required
def unread_message_counts():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({}), 401

    # Messages dont je suis PAS l'auteur et que je n'ai PAS lus
    count_by_channel = Message.get_unread_counts_by_channel(user_id)

    return jsonify({Ticket.find_by_channel_id(channel_id).id : count for channel_id, count in count_by_channel}), 200


# ── Marquer tous les messages d'un ticket comme lus ───────
@api_bp.route('/messages/mark-read', methods=['POST'])
@handle_db_errors
@login_required
def mark_message_as_read():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Non authentifié'}), 401

    data      = request.get_json()
    ticket = Ticket.find_by_id(data.get('ticket_id'))

    count_unread_msgs = Message.mark_channel_as_read(ticket.channel_id, user_id)

    return jsonify({'marked': count_unread_msgs}), 200