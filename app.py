from datetime import datetime, time
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tickets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


def get_utc_now():
    return datetime.utcnow()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)

    tickets = db.relationship("Ticket", back_populates="author", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="en_attente", nullable=False)
    admin_response = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", back_populates="tickets")


@app.before_request
def load_user():
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Vous devez être connecté pour accéder à cette page.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None or not g.user.is_admin:
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapped_view


def parse_deadline(value: str):
    if not value:
        return None

    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

    return datetime.combine(parsed_date, time.max)


def format_countdown(deadline: datetime, reference: datetime) -> str:
    seconds_left = int((deadline - reference).total_seconds())
    days = abs(seconds_left) // 86400
    hours = (abs(seconds_left) % 86400) // 3600

    if seconds_left >= 0:
        return f"{days}j {hours}h restantes"
    return f"En retard de {days}j {hours}h"


@app.route("/")
def index():
    status = request.args.get("status", "all")
    sort = request.args.get("sort", "recent")
    q = request.args.get("q", "").strip()
    author = request.args.get("author", "").strip()
    overdue_only = request.args.get("overdue", "0") == "1"
    now = get_utc_now()

    query = Ticket.query.join(User)

    if status != "all":
        query = query.filter(Ticket.status == status)

    if q:
        query = query.filter((Ticket.title.ilike(f"%{q}%")) | (Ticket.content.ilike(f"%{q}%")))

    if author:
        query = query.filter(User.username.ilike(f"%{author}%"))

    if overdue_only:
        query = query.filter(Ticket.deadline.isnot(None), Ticket.deadline < now, Ticket.status != "resolu")

    if sort == "oldest":
        query = query.order_by(Ticket.created_at.asc())
    else:
        query = query.order_by(Ticket.created_at.desc())

    tickets = query.all()

    return render_template(
        "index.html",
        tickets=tickets,
        now=now,
        format_countdown=format_countdown,
        current_status=status,
        current_sort=sort,
        current_q=q,
        current_author=author,
        current_overdue=overdue_only,
    )


@app.route("/register", methods=["GET", "POST"])
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


@app.route("/login", methods=["GET", "POST"])
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


@app.route("/logout")
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("index"))


@app.route("/profile")
@login_required
def profile():
    return redirect(url_for("user_profile", user_id=g.user.id))


@app.route("/users/<int:user_id>", methods=["GET", "POST"])
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


@app.route("/tickets/new", methods=["GET", "POST"])
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


@app.route("/tickets/<int:ticket_id>/edit", methods=["GET", "POST"])
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


@app.route("/tickets/<int:ticket_id>/admin", methods=["POST"])
@admin_required
def admin_update_ticket(ticket_id: int):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        flash("Ticket introuvable.", "danger")
        return redirect(url_for("index"))

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
    return redirect(url_for("index"))


@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    print("Base de données initialisée.")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
