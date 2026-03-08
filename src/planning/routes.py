

from flask import jsonify, request, g, render_template, flash
from src.models import Task, User
from src.utils import login_required, admin_required, send_notification
from . import plan_bp


@plan_bp.route("/")
def see_planning():
    send_notification(g.user.id, "feur", "osef")
    tasks = Task.find_all()
    if tasks is not None:
        assigns={}
        for task in tasks:
            assign = Task.find_all_childs_asssign(task.id)
            names=""
            for participent in assign:
                user= User.find_by_id(participent)
                names+= user.username + ","
            assigns[task.id]= names
    return render_template("planning.html", planning=Task.find_all(), personnes=assigns)

@plan_bp.route("/addTask", methods=["POST"])
@login_required
def addTask():
    """Pour Ajouter une tache"""
    parent_id = request.args.get("parent_id")
    title = request.form.get("title", "")
    content = request.form.get("content", "")

    try:
        task = Task.create_Task(
            title=title,
            content=content,
            user_id=g.user.id,
            parent_id=parent_id)
        return jsonify({
            "id": task.id,
            "title": task.title,
            "content": task.content,
            "status": task.status,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@plan_bp.route("/<int:task_id>/status", methods=["PATCH"])
def UpdateTaskStatus(task_id: int):
    task = Task.find_by_id(task_id)
    if task is None:
        flash("la tache n'existe pas", "warning")
        return jsonify({"success": False, "error": "Task non trouvée"}), 404
    data = request.get_json()
    task.update_status(data["status"])
    parent = Task.find_parent_by_parent_id(task.parent_id)
    if parent is not None:
        return jsonify({
            "success": True,
            "parent_id": parent.id
            }), 200
    else:
        return jsonify({
            "success": True
            }), 200



@plan_bp.route("/<int:task_id>/update", methods=["GET", "POST"])
def update(task_id):
    task = Task.find_by_id(task_id)
    if task is None:
        return jsonify({"success": False, "error": "Task non trouvée"}), 404
    if request.method == "GET":
        return jsonify({
            "success": True,
            "title": task.title,
            "content": task.content
        }), 200
    else:
        title = request.form.get("title", "")
        content = request.form.get("content", "")
        task.update(title=title, content=content)
        return jsonify({
            "success": True}), 200


@plan_bp.route("/<int:task_id>/delete", methods=["DELETE"])
@admin_required
def delete(task_id):
    task = Task.find_by_id(task_id)
    if task is None:
        return jsonify({"success": False, "error": "Task non trouvée"}), 404
    if g.user.id == task.author_id or g.user.is_admin_user():
        task.delete_Task()
        return jsonify({
            "success": True}), 200
    else:
        return jsonify({"success": False, 
                        "error": "Vous n'avez pas la permission de suppprimer cette task"}), 404