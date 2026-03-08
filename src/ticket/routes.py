from datetime import timezone

from flask import flash, g, redirect, render_template, request, url_for, jsonify

from src.models import Ticket, User, Channel
from src.models.database import db
from src.ticket.utils import format_countdown, is_deadline_late, parse_deadline
from src.utils import send_notification, get_utc_now, login_required

from . import ticket_bp


@ticket_bp.route("/<int:ticket_id>/update_status", methods=["POST"])
@login_required
def status_update_ticket(ticket_id: int):
    ticket = Ticket.find_by_id(ticket_id)
    if ticket is None:
        flash("Ticket introuvable.", "danger")
        return redirect(url_for("index"))

    status = request.form.get("status", ticket.status)

    allowed_statuses = {"en_attente", "en_cours", "resolu"}
    if status not in allowed_statuses:
        flash("Statut invalide.", "danger")
        return redirect(url_for("index"))

    ticket.update(status=status)

    send_notification(
        user_id=ticket.author_id,
        message=f"Votre ticket « {ticket.title} » est {status}",
        notification_type="statut",
        ticket_id=ticket.id
    )

    flash("Ticket mis à jour.", "success")
    return redirect(url_for("ticket.manage_ticket"))


@ticket_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_ticket():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        categorie = request.form.get("categorie", "").strip()
        content = request.form.get("content", "").strip()
        deadline_input = request.form.get("deadline", "").strip()
        deadline = parse_deadline(deadline_input)

        if not title or not content:
            flash("Le titre et le contenu sont obligatoires.", "danger")
            return redirect(url_for("ticket.create_ticket"))

        if deadline_input and deadline is None:
            flash("Format de date limite invalide.", "danger")
            return redirect(url_for("ticket.create_ticket"))

        if not hasattr(g, "user") or g.user is None:
            flash("Utilisateur introuvable.", "danger")
            return redirect(url_for("auth.login"))


        ticket = Ticket.create(title=title, categorie=categorie, content=content, deadline=deadline, author=g.user)

        channel = Channel.create(name=f"Discussion ticket #{ticket.id}")
        
        ticket.update(channel_id = channel.id) # necessaire car on modife le ticket avec l'ajout de la clef etrangere channel _id

        flash("Ticket créé avec succès.", "success")
        return redirect(url_for("ticket.manage_ticket"))

    return render_template("create_ticket.html")


@ticket_bp.route("/<int:ticket_id>/edit", methods=["GET", "POST"])
@login_required
def edit_ticket(ticket_id: int):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        return jsonify({"sucess": False, "error": "Ticket introuvable"}), 404

    if not hasattr(g, "user") or g.user is None:
        return jsonify({"sucess": False, 
                        "error": "Utilisateur introuvable"}), 404

    if ticket.author_id != g.user.id:
        return jsonify({
            "sucess": False, 
            "error": "Vous ne pouvez modifier que vos propres tickets"}), 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Le titre et le contenu sont obligatoires.", "danger")
            return redirect(url_for("ticket.edit_ticket", ticket_id=ticket_id))

        ticket.update(title=title, content=content)
        return jsonify({
            "success": True}), 200
    else:

        return jsonify({
            "success": True,
            "title": ticket.title,
            "content": ticket.content
        }), 200

@ticket_bp.route("/")
def manage_ticket():
    """Affiche la liste des tickets avec filtres, recherche et tri."""
    status = request.args.get("status", "all")
    sort = request.args.get("sort", "recent")
    categorie = request.args.get("categorie", "all")
    q = request.args.get("q", "").strip()
    author = request.args.get("author", "").strip()

    query = Ticket.query.join(User)

    if status != "all":
        query = query.filter(Ticket.status == status)

    if categorie != "all":
        query = query.filter(Ticket.categorie == categorie) 

    if q:
        query = query.filter(
            (Ticket.title.ilike(f"%{q}%")) | (Ticket.content.ilike(f"%{q}%"))
        )

    if author:
        query = query.filter(User.username.ilike(f"%{author}%"))

    if sort == "oldest":
        query = query.order_by(Ticket.created_at.asc())
    else:
        query = query.order_by(Ticket.created_at.desc())

    tickets = query.all()

    now = get_utc_now().astimezone(timezone.utc)

    return render_template(
        "manage_tickets.html",
        tickets=tickets,
        current_status=status,
        current_sort=sort,
        current_categorie=categorie,
        current_q=q,
        current_author=author,
        now=now,
        format_countdown=format_countdown,
        is_deadline_late=is_deadline_late,
    )
