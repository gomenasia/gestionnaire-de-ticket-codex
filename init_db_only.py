"""
Script minimal pour créer les tables sur PostgreSQL Railway.
Usage:
    railway run python init_db_only.py
"""
import os
import sys

db_url = os.environ.get("DATABASE_URL", "")
if not db_url:
    print("❌ DATABASE_URL non définie !")
    sys.exit(1)

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

print(f"🔌 Connexion à : {db_url[:40]}...")

# On injecte DATABASE_URL proprement dans l'environnement
os.environ["DATABASE_URL"] = db_url
os.environ["FLASK_CONFIG"] = "production"
os.environ["SECRET_KEY"] = os.environ.get("SECRET_KEY", "tmp-init-key")

from flask import Flask
from src.models.database import db

# Import de TOUS les modèles pour que SQLAlchemy les connaisse
from src.models.user import User
from src.models.ticket import Ticket
from src.models.task import Task
from src.models.channel import Channel
from src.models.message import Message
from src.models.notification import Notification

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

db.init_app(app)

with app.app_context():
    print("⏳ Création des tables...")
    try:
        db.create_all()
        print("✅ Tables créées avec succès !")

        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables présentes ({len(tables)}) : {tables}")
    except Exception as e:
        print(f"💥 Erreur : {e}")
        sys.exit(1)
