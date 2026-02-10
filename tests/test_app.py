import tempfile

import pytest

<<<<<<< HEAD
from app import app, db, User, Ticket
=======
from app import Ticket, User, app, db
>>>>>>> 23263c0de9d4f925ff941a244cb4ff6efc0d7eed


@pytest.fixture
def client():
<<<<<<< HEAD
    db_fd, db_path = tempfile.mkstemp()
=======
    _, db_path = tempfile.mkstemp()
>>>>>>> 23263c0de9d4f925ff941a244cb4ff6efc0d7eed
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


def test_register_login_and_create_ticket(client):
    response = register(client)
    assert b"Compte cr" in response.data

    response = login(client)
    assert b"Connexion r" in response.data

    response = client.post(
        "/tickets/new",
        data={"title": "Bug API", "content": "Erreur 500"},
        follow_redirects=True,
    )

    assert b"Ticket cr" in response.data
    assert b"Bug API" in response.data


<<<<<<< HEAD
=======
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

    response = client.get("/profile")
    assert b"Mon profil" in response.data
    assert b"Nombre de tickets" in response.data

    response = client.post(
        "/profile",
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


>>>>>>> 23263c0de9d4f925ff941a244cb4ff6efc0d7eed
def test_admin_can_update_ticket(client):
    register(client)
    login(client)
    client.post("/tickets/new", data={"title": "A", "content": "B"}, follow_redirects=True)

    with app.app_context():
        admin = User(username="admin", email="admin@example.com", is_admin=True)
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
