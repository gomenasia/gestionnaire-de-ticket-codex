# Gestionnaire de tickets

Application web Flask de gestion de demandes (tickets) avec :

- Inscription / connexion des utilisateurs.
- Création de tickets uniquement pour les utilisateurs connectés.
- Modification du **propre** ticket (titre + description) par son auteur.
- Gestion des tickets (statut + réponse) uniquement par les admins.
- Barre de filtres horizontale sur la page principale avec :
  - filtre par statut (`en_attente`, `en_cours`, `resolu`),
  - tri (`recent`, `oldest`),
  - recherche texte dans le contenu/titre,
  - recherche par auteur.
- Menu compte déroulant au survol (profil + déconnexion).
- Page profil avec : nom, email, rôle admin, nombre de tickets, changement de mot de passe.
- Stockage SQL via SQLite (remplaçable par un autre SGBD SQL via URI).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer l'application

```bash
flask --app app run
```

L'application sera disponible sur `http://127.0.0.1:5000`.

## Initialiser la base

La base est créée automatiquement au lancement. Commande disponible aussi :

```bash
flask --app app init-db
```

## Tests

```bash
pip install pytest
pytest
```

## Rendre un utilisateur admin

Exemple rapide dans un shell Flask :

```bash
flask --app app shell
```

Puis :

```python
from app import db, User
u = User.query.filter_by(email="admin@example.com").first()
u.is_admin = True
db.session.commit()
```
