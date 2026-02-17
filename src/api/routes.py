"""API pour l'application."""

from flask import jsonify, request
from src.models import Ticket, User
from src.utils import get_utc_now
from . import api_bp

@api_bp.route("/tickets")
def api_tickets():
    """API pour récupérer les tickets filtrés en JSON."""
    
    status = request.args.get("status", "all")
    sort = request.args.get("sort", "recent")
    q = request.args.get("q", "").strip()
    author = request.args.get("author", "").strip()
    now = get_utc_now()

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