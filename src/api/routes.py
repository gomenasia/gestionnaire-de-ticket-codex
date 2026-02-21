"""API pour l'application."""

from flask import jsonify, request, g
from src.models import Ticket, User, Task
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


@api_bp.route("/<int:parent_id>/addTask", methods=["POST"])
@login_required
def addTask(parent_id: int):
    """Pour Ajouter une tache"""
    title = request.form.get("title", "")
    content = request.form.get("content", "recent")

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
