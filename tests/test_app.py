import tempfile

import pytest

from datetime import datetime, timedelta, timezone
from app import Ticket, User, app, db
from src.ticket.utils import format_countdown, is_deadline_late


@pytest.fixture
def client():
    _, db_path = tempfile.mkstemp()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def register(client, username="alice", email="alice@example.com", password="secret"):
    return client.post(
        "/register",
        data={"username": username, "email": email, "password": password},
        follow_redirects=True,
    )


def login(client, email="alice@example.com", password="secret"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_register_login_and_create_ticket_with_deadline(client):
    register(client)
    login(client)

    response = client.post(
        "/tickets/new",
        data={"title": "Bug API", "content": "Erreur 500", "deadline": "2030-01-01"},
        follow_redirects=True,
    )

    assert b"Ticket cr" in response.data
    assert b"Bug API" in response.data
    assert b"\xc3\x89ch\xc3\xa9ance" in response.data


def test_author_can_edit_own_ticket(client):
    register(client)
    login(client)
    client.post("/tickets/new", data={"title": "Ancien", "content": "Desc"}, follow_redirects=True)

    with app.app_context():
        ticket = Ticket.query.first()

    response = client.post(
        f"/tickets/{ticket.id}/edit",
        data={"title": "Nouveau titre", "content": "Nouvelle description"},
        follow_redirects=True,
    )

    assert b"Ticket modifi" in response.data
    assert b"Nouveau titre" in response.data


def test_profile_and_password_update(client):
    register(client)
    login(client)

    response = client.get("/profile", follow_redirects=True)
    assert b"Profil de alice" in response.data
    assert b"Nombre de tickets" in response.data

    response = client.post(
        "/users/1",
        data={"current_password": "secret", "new_password": "new-secret"},
        follow_redirects=True,
    )
    assert b"Mot de passe mis" in response.data

    client.get("/logout", follow_redirects=True)
    response = client.post(
        "/login",
        data={"email": "alice@example.com", "password": "new-secret"},
        follow_redirects=True,
    )
    assert b"Connexion r" in response.data


def test_user_profile_shows_user_tickets_and_author_link(client):
    register(client)
    login(client)

    client.post("/tickets/new", data={"title": "Ticket A", "content": "Alpha"}, follow_redirects=True)
    client.post("/tickets/new", data={"title": "Ticket B", "content": "Beta"}, follow_redirects=True)

    with app.app_context():
        alice = User.query.filter_by(email="alice@example.com").first()

    response = client.get("/")
    assert f'/users/{alice.id}'.encode() in response.data

    response = client.get(f"/users/{alice.id}")
    assert b"Ticket A" in response.data
    assert b"Ticket B" in response.data


def test_cannot_change_password_on_other_profile(client):
    register(client)
    login(client)
    register(client, username="bob", email="bob@example.com", password="secret")

    with app.app_context():
        bob = User.query.filter_by(email="bob@example.com").first()

    response = client.post(
        f"/users/{bob.id}",
        data={"current_password": "secret", "new_password": "new-secret"},
        follow_redirects=True,
    )

    assert b"ne pouvez modifier le mot de passe" in response.data


def test_admin_can_update_ticket(client):
    register(client)
    login(client)
    client.post("/tickets/new", data={"title": "A", "content": "B"}, follow_redirects=True)

    with app.app_context():
        admin = User(username="admin", email="admin@example.com", role = "admin")
        admin.set_password("secret")
        db.session.add(admin)
        db.session.commit()
        ticket = Ticket.query.first()

    client.get("/logout", follow_redirects=True)
    client.post("/login", data={"email": "admin@example.com", "password": "secret"}, follow_redirects=True)
    response = client.post(
        f"/tickets/{ticket.id}/admin",
        data={"status": "resolu", "admin_response": "Corrigé"},
        follow_redirects=True,
    )

    assert b"Ticket mis" in response.data
    assert b"Corrig" in response.data


def test_deadline_helpers_handle_mixed_timezone_datetimes():
    deadline_aware = datetime(2030, 1, 2, 0, 0, tzinfo=timezone.utc)
    reference_naive = datetime(2030, 1, 1, 23, 0)

    assert format_countdown(deadline_aware, reference_naive) == "0j 1h restantes"
    assert is_deadline_late(reference_naive, deadline_aware) is True
