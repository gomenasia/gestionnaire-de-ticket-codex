"""API pour l'application."""

from flask import jsonify, request, g, session
from src.models import Ticket, User, Task, Message
from src.utils import login_required
from . import api_bp


@api_bp.route("/tickets")
def api_tickets():
    """API pour récupérer les tickets filtrés en JSON."""
    
    status = request.args.get("status", "all")
    sort = request.args.get("sort", "recent")
    q = request.args.get("q", "").strip()
    author = request.args.get("author", "").strip()

    query = Ticket.query.join(User)

    if status != "all":
        query = query.filter(Ticket.status == status)

    if q:
        query = query.filter((Ticket.title.ilike(f"%{q}%")) | (Ticket.content.ilike(f"%{q}%")))

    if author:
        query = query.filter(User.username.ilike(f"%{author}%"))

    if sort == "oldest":
        query = query.order_by(Ticket.created_at.asc())
    else:
        query = query.order_by(Ticket.created_at.desc())

    tickets = query.all()

    # Convertir les tickets en dictionnaire
    tickets_data = []
    for ticket in tickets:
        ticket_dict = {
            "id": ticket.id,
            "title": ticket.title,
            "content": ticket.content,
            "status": ticket.status,
            "priority": ticket.priority,
            "created_at": ticket.created_at.isoformat(),
            "deadline": ticket.deadline.isoformat() if ticket.deadline else None,
            "author": {
                "id": ticket.author.id,
                "username": ticket.author.username,
            },
            # Ajoutez d'autres champs selon vos besoins
        }
        tickets_data.append(ticket_dict)

    return jsonify({
        "tickets": tickets_data,
        "count": len(tickets_data)
    })


@api_bp.route("/addTask", methods=["POST"])
@login_required
def addTask():
    """Pour Ajouter une tache"""
    parent_id = request.args.get("parent_id")
    title = request.form.get("title", "")
    content = request.form.get("content", "")

    try:
        task = Task.create_Task(
            title=title,
            content=content,
            user_id=g.user.id,
            parent_id=parent_id)
        return jsonify({
            "id": task.id,
            "title": task.title,
            "content": task.content,
            "status": task.status,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/task/<int:task_id>/status", methods=["PATCH"])
def UpdateTaskStatus(task_id: int):
    task = Task.find_by_id(task_id)
    if task is None:
        return jsonify({"success": False, "error": "Task non trouvée"}), 404
    data = request.get_json()
    task.update_status(data["status"])
    parent = Task.find_parent_by_parent_id(task.parent_id)
    if parent is not None:
        return jsonify({
            "success": True,
            "parent_id": parent.id
            }), 200
    else:
        return jsonify({
            "success": True
            }), 200


@api_bp.route("/channel/<int:channel_id>/messages")
@login_required
def get_messages(channel_id):
    since = request.args.get("since", 0)
    messages = Message.query.filter(
        Message.channel_id == channel_id,
        Message.id > since
    ).all()
    return jsonify([m.to_dict() for m in messages])


@api_bp.route("/task/<int:task_id>/update", methods=["GET", "POST"])
def update(task_id):
    task = Task.find_by_id(task_id)
    if task is None:
        return jsonify({"success": False, "error": "Task non trouvée"}), 404
    if request.method == "GET":
        return jsonify({
            "success": True,
            "title": task.title,
            "content": task.content
        }), 200
    else:
        title = request.form.get("title", "")
        content = request.form.get("content", "")
        task.update(title=title, content=content)
        return jsonify({
            "success": True}), 200


@api_bp.route("/task/<int:task_id>/delete", methods=["DELETE"])
def delete(task_id):
    task = Task.find_by_id(task_id)
    if task is None:
        return jsonify({"success": False, "error": "Task non trouvée"}), 404
    if g.user.id == task.author_id or g.user.is_admin_user():
        task.delete_Task()
        return jsonify({
            "success": True}), 200
    else:
        return jsonify({"success": False, 
                        "error": "Vous n'avez pas la permission de suppprimer cette task"}), 404

@api_bp.route('/session')
def get_session():
    return jsonify({
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role')
    })