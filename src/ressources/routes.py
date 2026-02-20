from flask import render_template
from . import ressources_bp

@ressources_bp.route("/")
def ressource_hub():
    return render_template("ressources_hub.html")