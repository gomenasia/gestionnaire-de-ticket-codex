from flask import flash, g, redirect, render_template, request, url_for

from src.models import User, Ticket
from src.ticket.services import parse_deadline, format_countdown
fr
from src.models.database import db

from . import ticket_bp


@ticket_bp.route("/<int:ticket_id>/admin", methods=["POST"])
@admin_required
def admin_update_ticket(ticket_id: int):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        flash("Ticket introuvable.", "danger")
        return redirect(url_for("ticket.index"))

    status = request.form.get("status", ticket.status)
    admin_response = request.form.get("admin_response", "").strip()

    allowed_statuses = {"en_attente", "en_cours", "resolu"}
    if status not in allowed_statuses:
        flash("Statut invalide.", "danger")
        return redirect(url_for("index"))

    ticket.status = status
    ticket.admin_response = admin_response or None
    db.session.commit()

    flash("Ticket mis à jour.", "success")
    return redirect(url_for("ticket.index"))


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
            return redirect(url_for("create_ticket"))

        if deadline_input and deadline is None:
            flash("Format de date limite invalide.", "danger")
            return redirect(url_for("create_ticket"))

        ticket = Ticket(title=title, content=content, deadline=deadline, author=g.user)
        db.session.add(ticket)
        db.session.commit()

        flash("Ticket créé avec succès.", "success")
        return redirect(url_for("index"))

    return render_template("create_ticket.html")


@ticket_bp.route("/tickets/<int:ticket_id>/edit", methods=["GET", "POST"])
@login_required
def edit_ticket(ticket_id: int):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        flash("Ticket introuvable.", "danger")
        return redirect(url_for("index"))

    if ticket.author_id != g.user.id:
        flash("Vous ne pouvez modifier que vos propres tickets.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Le titre et le contenu sont obligatoires.", "danger")
            return redirect(url_for("edit_ticket", ticket_id=ticket_id))

        ticket.title = title
        ticket.content = content
        db.session.commit()
        flash("Ticket modifié avec succès.", "success")
        return redirect(url_for("index"))

    return render_template("edit_ticket.html", ticket=ticket)