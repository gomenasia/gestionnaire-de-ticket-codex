from flask import flash, g, redirect, render_template, request, url_for

from src.models import Ticket, User
from src.models.database import db
from src.ticket.utils import parse_deadline, format_countdown
from src.utils import admin_required, login_required, get_utc_now

from . import ticket_bp


@ticket_bp.route("/<int:ticket_id>/admin", methods=["POST"])
@admin_required
def admin_update_ticket(ticket_id: int):
    ticket = Ticket.find_by_id(ticket_id)
    if ticket is None:
        flash("Ticket introuvable.", "danger")
        return redirect(url_for("index"))

    status = request.form.get("status", ticket.status)
    admin_response = request.form.get("admin_response", "").strip()

    allowed_statuses = {"en_attente", "en_cours", "resolu"}
    if status not in allowed_statuses:
        flash("Statut invalide.", "danger")
        return redirect(url_for("index"))

    ticket.update(status=status, admin_response=admin_response or None)

    flash("Ticket mis à jour.", "success")
    return redirect(url_for("index"))


@ticket_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_ticket():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
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

        Ticket.create(title=title, content=content, deadline=deadline, author=g.user)

        flash("Ticket créé avec succès.", "success")
        return redirect(url_for("ticket.manage_ticket"))

    return render_template("create_ticket.html")


@ticket_bp.route("/<int:ticket_id>/edit", methods=["GET", "POST"])
@login_required
def edit_ticket(ticket_id: int):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        flash("Ticket introuvable.", "danger")
        return redirect(url_for("index"))

    if not hasattr(g, "user") or g.user is None:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("auth.login"))

    if ticket.author_id != g.user.id:
        flash("Vous ne pouvez modifier que vos propres tickets.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Le titre et le contenu sont obligatoires.", "danger")
            return redirect(url_for("ticket.edit_ticket", ticket_id=ticket_id))

        ticket.title = title
        ticket.content = content
        db.session.commit()
        flash("Ticket modifié avec succès.", "success")
        return redirect(url_for("ticket.manage_ticket"))

    return render_template("edit_ticket.html", ticket=ticket)


@ticket_bp.route("/")
def manage_ticket():
    """Affiche la liste des tickets avec filtres, recherche et tri."""
    status = request.args.get("status", "all")
    sort = request.args.get("sort", "recent")
    q = request.args.get("q", "").strip()
    author = request.args.get("author", "").strip()
    now = get_utc_now()

    query = Ticket.query.join(User)

    if status != "all":
        query = query.filter(Ticket.status == status)

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

    return render_template(
        "manage_tickets.html",
        tickets=tickets,
        now=now,
        current_status=status,
        current_sort=sort,
        current_q=q,
        current_author=author,
        format_countdown=format_countdown,
    )
