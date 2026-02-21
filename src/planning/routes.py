from flask import render_template


from . import plan_bp
from src.models import Task


@plan_bp.route("/")
def see_planning():
    return render_template("planning.html", planning=Task.find_all())
