from werkzeug.security import check_password_hash, generate_password_hash
from flask import flash, g, redirect, render_template, request, session, url_for

from src.models import User

from . import auth_bp


def set_password(self, password: str) -> None:
    self.password_hash = generate_password_hash(password)


def check_password(self, password: str) -> bool:
    return check_password_hash(self.password_hash, password)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for("register"))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Nom d'utilisateur ou email déjà utilisé.", "danger")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Compte créé avec succès. Connectez-vous.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash("Identifiants invalides.", "danger")
            return redirect(url_for("login"))

        session.clear()
        session["user_id"] = user.id
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
    return redirect(url_for("user_profile", user_id=g.user.id))


@auth_bp.route("/users/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_profile(user_id: int):
    profile_user = db.session.get(User, user_id)
    if profile_user is None:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("index"))

    is_own_profile = g.user.id == profile_user.id

    if request.method == "POST":
        if not is_own_profile:
            flash("Vous ne pouvez modifier le mot de passe que sur votre propre profil.", "danger")
            return redirect(url_for("user_profile", user_id=user_id))

        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")

        if not current_password or not new_password:
            flash("Veuillez renseigner l'ancien et le nouveau mot de passe.", "danger")
            return redirect(url_for("user_profile", user_id=user_id))

        if not g.user.check_password(current_password):
            flash("Mot de passe actuel invalide.", "danger")
            return redirect(url_for("user_profile", user_id=user_id))

        g.user.set_password(new_password)
        db.session.commit()
        flash("Mot de passe mis à jour.", "success")
        return redirect(url_for("user_profile", user_id=user_id))

    user_tickets = Ticket.query.filter_by(author_id=profile_user.id).order_by(Ticket.created_at.desc()).all()
    ticket_count = len(user_tickets)
    return render_template(
        "profile.html",
        profile_user=profile_user,
        ticket_count=ticket_count,
        user_tickets=user_tickets,
        is_own_profile=is_own_profile,
    )