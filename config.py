"""
Configuration pour l'application Flask.
Approche classique Flask avec classes de configuration.
Support des fichiers .env pour les variables d'environnement.
"""

import os
from pathlib import Path
from typing import Type


# Répertoire de base du projet (où se trouve config.py)
BASE_DIR = Path(__file__).resolve().parent


def _get_database_uri() -> str:
    """Récupère l'URI de la base de données et convertit les chemins SQLite relatifs en absolus."""
    db_url = os.environ.get("DATABASE_URL") or "sqlite:///app.db"

    # Si c'est une URI SQLite avec un chemin relatif (3 slashes), la convertir en absolu
    if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:////"):
        # Extraire le chemin relatif après sqlite:///
        relative_path = db_url.replace("sqlite:///", "")
        # Construire le chemin absolu
        absolute_path = BASE_DIR / relative_path
        # Retourner l'URI avec 4 slashes pour un chemin absolu
        return f"sqlite:///{absolute_path}"

    return db_url


class Config:
    """Configuration de base."""

    SECRET_KEY: str = (
        os.environ.get("SECRET_KEY") or "cle-secrete-dev-non-securisee"
    )
    SQLALCHEMY_DATABASE_URI: str = _get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


class DevelopmentConfig(Config):
    """Configuration pour le développement."""

    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = True  # Affiche les requêtes SQL dans la console


class TestingConfig(Config):
    """Configuration pour les tests."""

    TESTING: bool = True
    DEBUG: bool = False
    # Base de données en mémoire
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Configuration pour la production."""

    DEBUG: bool = False
    SQLALCHEMY_ECHO: bool = False

    def __init__(self) -> None:
        """Initialise la config production avec vérifications."""
        # En production, SECRET_KEY DOIT être définie
        secret: str | None = os.environ.get("SECRET_KEY")
        if not secret:
            raise ValueError("SECRET_KEY doit être définie en production")
        self.SECRET_KEY = secret


# Dictionnaire de configuration
config: dict[str, Type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}