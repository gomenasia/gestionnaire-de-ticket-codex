import tempfile

import pytest

from app import app, db, User, Ticket


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
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
