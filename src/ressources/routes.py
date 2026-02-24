from flask import render_template
from . import ressources_bp

@ressources_bp.route("/tp")
def ressource_tp():
    return render_template("ressource_tp.html")

@ressources_bp.route("/cm")
def ressource_cm():
    return render_template("ressource_cm.html")

@ressources_bp.route("/projet")
def ressource_projet():
    return render_template("ressource_projet.html")
