#!/usr/bin/env python3
"""
Script de lancement pour différents environnements.
Facilite le changement d'environnement pour les étudiants.
"""

import os
import subprocess
import sys


def main() -> None:
    """Point d'entrée principal."""
    if len(sys.argv) != 2:
        print("Usage: python run.py [development|production]")
        print("\nExemples:")
        print("  python run.py development  # Lance en mode développement")
        print("  python run.py production   # Lance en mode production")
        sys.exit(1)

    env_name: str = sys.argv[1].lower()

    if env_name not in ["development", "production"]:
        print(
            "❌ Environnement invalide. Utilisez 'development' ou 'production'"
        )
        sys.exit(1)


    # Lancer l'application
    print(f"🚀 Lancement en mode {env_name.upper()}...")

    if env_name == "development":
        print("📍 URL: http://localhost:5000")
        os.system("flask run --reload")
    else:
        print("📍 Mode production - Lancement avec Gunicorn")
        print("📍 URL: http://localhost:8000")

        # Activer l'environnement virtuel et lancer gunicorn
        venv_activate: str = os.path.join(
            os.getcwd(), "..", ".venv", "bin", "activate"
        )
        if os.path.exists(venv_activate):
            # Utiliser subprocess pour gérer correctement les espaces
            cmd: str = (
                f'source "{venv_activate}" && gunicorn --bind 0.0.0.0:8000 --workers 4 app:app'
            )
            subprocess.run(
                cmd, shell=True, executable="/bin/bash", check=False
            )
        else:
            print(
                "⚠️ Environnement virtuel non trouvé, tentative avec gunicorn global"
            )
            os.system("gunicorn --bind 0.0.0.0:8000 --workers 4 app:app")


if __name__ == "__main__":
    main()
