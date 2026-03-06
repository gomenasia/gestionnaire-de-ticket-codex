import re
from typing import Optional

from flask import flash, g, jsonify, redirect, render_template, request, session, url_for

from src.models import Ticket, User
from src.utils import expects_json_response, login_required

from . import auth_bp


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fields = {
            "username": request.form.get("username", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "password": request.form.get("password", ""),
        }

        if not all(fields.values()):
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for("auth.register"))

        if error := validEmail(fields["email"]):
            flash(error, "danger")
            return redirect(url_for("auth.register"))

        if error := validUsername(fields["username"]):
            flash(error, "danger")
            return redirect(url_for("auth.register"))

        try:
            User.create_user(**fields)
            user = User.find_by_email(fields["email"])

            if not user:
                flash("Erreur lors de la création du compte.", "danger")
                return redirect(url_for("auth.register"))

            session.clear()
            session["user_id"] = user.id
            session["role"] = user.role
            session["username"] = user.username

            flash("Compte créé avec succès. Connectez-vous.", "success")
            return redirect(url_for("index"))

        except Exception as e:
            print(f"Erreur lors de l'inscription: {e}")
            flash("Une erreur est survenue lors de la création du compte.", "danger")
            return redirect(url_for("auth.register"))

    if expects_json_response():
        return jsonify({"success": True, "message": "Utilisez POST pour créer un compte."}), 200
    return render_template("register.html")


def validEmail(email: str) -> Optional[str]:
    EMAIL_RE = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(EMAIL_RE, email):
        return "Format e-mail invalide"
    if User.find_by_email(email):
        return "E-mail déjà utilisé"
    return None


def validUsername(username: str) -> Optional[str]:
    USERNAME_RE = r"^[a-z0-9]{3,64}$"
    if not re.match(USERNAME_RE, username):
        return "Nom d'utilisateur invalide"
    if User.find_by_username(username):
        return "L'utilisateur existe déjà"
    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.find_by_email(email)
        if user is None or not user.check_password(password):
            flash("Identifiants invalides.", "danger")
            return redirect(url_for("auth.login"))

        session.clear()
        session["user_id"] = user.id
        session["role"] = user.role
        session["username"] = user.username
        flash("Connexion réussie.", "success")
        return redirect(url_for("index"))

    if expects_json_response():
        return jsonify({"success": True, "message": "Utilisez POST pour vous connecter."}), 200
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    if expects_json_response():
        return jsonify({"success": True, "message": "Vous êtes déconnecté."}), 200
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("index"))


@auth_bp.route("/profile")
@login_required
def profile():
    if not hasattr(g, "user") or g.user is None:
        if expects_json_response():
            return jsonify({"success": False, "error": "Utilisateur introuvable."}), 404
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("index"))

    if expects_json_response():
        return jsonify({"success": True, "redirect": url_for("auth.user_profile", user_id=g.user.id)}), 200
    return redirect(url_for("auth.user_profile", user_id=g.user.id))


@auth_bp.route("/users/<int:user_id>", methods=["POST"])
@login_required
def update_profile(user_id: int):
    profile_user = User.find_by_id(user_id)
    if profile_user is None or not hasattr(g, "user") or g.user is None:
        if expects_json_response():
            return jsonify({"success": False, "error": "Utilisateur introuvable."}), 404
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("index"))

    is_own_profile = g.user.id == profile_user.id

    if not is_own_profile:
        if expects_json_response():
            return jsonify({"success": False, "error": "Vous ne pouvez modifier le mot de passe que sur votre propre profil."}), 403
        flash("Vous ne pouvez modifier le mot de passe que sur votre propre profil.", "danger")
        return redirect(url_for("auth.user_profile", user_id=user_id))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")

    if not all([current_password, new_password]):
        if expects_json_response():
            return jsonify({"success": False, "error": "Veuillez renseigner l'ancien et le nouveau mot de passe."}), 400
        flash("Veuillez renseigner l'ancien et le nouveau mot de passe.", "danger")
        return redirect(url_for("auth.user_profile", user_id=user_id))

    if not g.user.check_password(current_password):
        if expects_json_response():
            return jsonify({"success": False, "error": "Mot de passe actuel invalide."}), 400
        flash("Mot de passe actuel invalide.", "danger")
        return redirect(url_for("auth.user_profile", user_id=user_id))

    profile_user.set_password(new_password)
    profile_user.save()
    if expects_json_response():
        return jsonify({"success": True, "message": "Mot de passe mis à jour."}), 200
    flash("Mot de passe mis à jour.", "success")
    return redirect(url_for("auth.user_profile", user_id=user_id))


@auth_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
def user_profile(user_id: int):
    profile_user = User.find_by_id(user_id)
    if profile_user is None or not hasattr(g, "user") or g.user is None:
        if expects_json_response():
            return jsonify({"success": False, "error": "Utilisateur introuvable."}), 404
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("index"))

    is_own_profile = g.user.id == profile_user.id

    user_tickets = Ticket.find_all_by_user(profile_user.id)
    ticket_count = len(user_tickets)

    if expects_json_response():
        return jsonify(
            {
                "success": True,
                "user": profile_user.to_dict(),
                "ticket_count": ticket_count,
                "tickets": [ticket.to_dict() for ticket in user_tickets],
                "is_own_profile": is_own_profile,
            }
        ), 200

    return render_template(
        "profile.html",
        profile_user=profile_user,
        ticket_count=ticket_count,
        user_tickets=user_tickets,
        is_own_profile=is_own_profile,
    )


@auth_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if expects_json_response():
        return jsonify({"success": True, "message": "Paramètres utilisateur."}), 200
    return render_template("settings.html")

    # INCOMPLETE
