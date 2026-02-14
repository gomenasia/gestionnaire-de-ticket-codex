import re

from flask import flash, redirect, render_template, request, session, url_for
from typing import Optional

from src.models import User, Ticket
from src.utils import login_required
from src.auth.utils import get_current_user
from . import auth_bp


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fields = {"username": request.form.get("username", "").strip(),
                  "email": request.form.get("email", "").strip().lower(),
                  "password": request.form.get("password", "")}

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
            # Créer l'utilisateur
            User.create_user(**fields)
            
            # Récupérer l'utilisateur créé
            user = User.find_by_email(fields["email"])

            
            if not user:
                flash("Erreur lors de la création du compte.", "danger")
                return redirect(url_for("auth.register"))
            
            # Connecter l'utilisateur
            session.clear()
            session["user_id"] = user.id
            
            flash("Compte créé avec succès. Connectez-vous.", "success")
            return redirect(url_for("index"))
            
        except Exception as e:
            # Logger l'erreur pour le debug
            print(f"Erreur lors de l'inscription: {e}")
            flash("Une erreur est survenue lors de la création du compte.", "danger")
            return redirect(url_for("auth.register"))


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
        session["is_admin"] = user.is_admin_user()
        session["role"] = user.role
        session["username"] = user.username
        flash("Connexion réussie.", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("index"))


@auth_bp.route("/profile")
@login_required
def profile():
    current_user = get_current_user()
    return redirect(url_for("auth.user_profile", user_id= current_user.id))


@auth_bp.route("/users/<int:user_id>", methods=["POST"])
@login_required
def update_profile(user_id: int):

    profile_user = get_current_user()
    if profile_user is None:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("index"))

    is_own_profile = get_current_user().id == profile_user.id

    if request.method == "POST":
        if not is_own_profile:
            flash("Vous ne pouvez modifier le mot de passe que sur votre propre profil.", "danger")
            return redirect(url_for("auth.user_profile", user_id=user_id))

        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")

        if not all([current_password, new_password]):
            flash("Veuillez renseigner l'ancien et le nouveau mot de passe.", "danger")
            return redirect(url_for("auth.user_profile", user_id=user_id))

        if not g.user.check_password(current_password):
            flash("Mot de passe actuel invalide.", "danger")
            return redirect(url_for("auth.user_profile", user_id=user_id))

        profile_user.set_password(new_password)
        profile_user.save()
        flash("Mot de passe mis à jour.", "success")
        return redirect(url_for("auth.user_profile", user_id=user_id))

@auth_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
def user_profile(user_id: int):
    profile_user = get_current_user()
    if profile_user is None:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("index"))

    is_own_profile = get_current_user().id == profile_user.id

    user_tickets = Ticket.find_all_by_user(profile_user.id)
    ticket_count = len(user_tickets)
    return render_template(
        "profile.html",
        profile_user=profile_user,
        ticket_count=ticket_count,
        user_tickets=user_tickets,
        is_own_profile=is_own_profile,
    )