from flask import render_template


from . import plan_bp


@plan_bp.route("/")
def see_planning():
    return render_template("planning.html")