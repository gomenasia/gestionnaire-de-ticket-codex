from flask import jsonify, render_template

from src.utils import expects_json_response

from . import ressources_bp


@ressources_bp.route("/tp")
def ressource_tp():
    if expects_json_response():
        return jsonify({"success": True, "resource": "tp", "template": "ressource_tp.html"}), 200
    return render_template("ressource_tp.html")


@ressources_bp.route("/cm")
def ressource_cm():
    if expects_json_response():
        return jsonify({"success": True, "resource": "cm", "template": "ressource_cm.html"}), 200
    return render_template("ressource_cm.html")


@ressources_bp.route("/projet")
def ressource_projet():
    if expects_json_response():
        return jsonify({"success": True, "resource": "projet", "template": "ressource_projet.html"}), 200
    return render_template("ressource_projet.html")
