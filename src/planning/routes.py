from flask import jsonify, render_template

from src.models import Task
from src.utils import expects_json_response

from . import plan_bp


@plan_bp.route("/")
def see_planning():
    planning = Task.find_all()
    if expects_json_response():
        return jsonify({"success": True, "planning": [task.to_dict() for task in planning], "count": len(planning)}), 200
    return render_template("planning.html", planning=planning)
