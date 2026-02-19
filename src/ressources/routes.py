from flask import render_template
from . import ressources_bp

@ressources_bp.route("/")
def index():
    return render_template("ressources/index.html")