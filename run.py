#!/usr/bin/env python3
"""
Script de lancement pour différents environnements.
Facilite le changement d'environnement pour les étudiants.
"""
import sys
import subprocess


def main():
    if len(sys.argv) != 2:
        print("Usage: python run.py [dev|prod]")
        return

    mode = sys.argv[1]
    
    if mode == "dev":
        print("🚀 Mode DEV (Flask + SocketIO)")
        print("📍 URL: http://localhost:5000")
        subprocess.run([sys.executable, "app.py"])

    elif mode == "prod":
        print("🚀 Mode PROD (simulation Railway)")
        print("📍 URL: http://localhost:8000")

        subprocess.run([
            sys.executable,
            "-m",
            "gunicorn",
            "-k",
            "geventwebsocket.gunicorn.workers.GeventWebSocketWorker",
            "-w",
            "1",
            "-b",
            "127.0.0.1:8000",
            "app:app"
        ])

    else:
        print("❌ mode invalide")


if __name__ == "__main__":
    main()