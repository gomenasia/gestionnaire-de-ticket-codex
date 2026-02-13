"""Point d'entrée de l'application Flask pour la gestion des tickets.
Configure l'application, initialise la base de données, et définit les routes principales."""

import os

from flask import Flask, render_template, request, session

from config import config
from src.auth import auth_bp
from src.ticket import ticket_bp
from src.models import Ticket
from src.models.database import db


def getTickets() -> list[Ticket]:
    return Ticket.find_all()


def create_app() -> Flask:
    """Factory Flask pour créer l'application avec la config appropriée."""
    # Déterminer l'environnement
    config_name: str = os.environ.get("FLASK_CONFIG", "development")
    app: Flask = Flask(__name__, template_folder="src/templates")  # pylint: disable=redefined-outer-name
    # Configurer l'application avec la config choisie en fonction de l'environnement
    app.config.from_object(config[config_name])
    # Configurer Jinja2 pour un rendu plus propre, sinon erreurs HTML générées
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Initialisation de SQLAlchemy avec l'application Flask
    # ⚠️ Ne crée PAS les tables automatiquement
    # Pour créer et peupler les tables, exécutez : python3 -m datafixtures.import_all
    db.init_app(app)

    app.register_blueprint(ticket_bp)
    app.register_blueprint(auth_bp)

    return app


app = create_app()
""" # Affiche la map des URL de l'application au démarrage
for rule in app.url_map.iter_rules():
    print(
        f"Endpoint: {rule.endpoint}, Methods: {','.join(rule.methods)}, URL: {rule.rule}"
    ) """


@app.route("/")
def index():    
    """Affiche la page d'accueil avec la liste des tickets."""
    tickets = getTickets()
    return render_template("index.html", tickets=tickets)


@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    print("Base de données initialisée.")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
