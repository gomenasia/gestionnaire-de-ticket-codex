

from flask import jsonify, request, g, render_template, flash
from src.models import Task, User
from src.utils import login_required, admin_required, send_notification
from . import plan_bp


@plan_bp.route("/")
def see_planning():
    send_notification(g.user.id, "feur", "osef")
    all_tasks = Task.query.all()
    
    children_by_parent = {}
    for task in all_tasks:
        if task.parent_id:
            children_by_parent.setdefault(task.parent_id, []).append(task)
    
    parent_tasks = [t for t in all_tasks if not t.parent_id]
    
    # fonction récursive à l'intérieur car sinon il faudrait mettre le dic children_by_parnet dans les paramêtre et ça risque de prendre de la place
    def get_descendant_assigns(task_id):
        assigns = set()
        for child in children_by_parent.get(task_id, []):
            if child.assign_id:
                assigns.add(child.assign_id)
            assigns.update(get_descendant_assigns(child.id))
        return assigns
    
    all_assign_ids = set()#pour voir tout les utlisateurs qui sont assigné à une tache
    task_assigns = {}#dictionnare qui stocke l'id de la tache et l'id des assigné de ces sous taches  ou de lui même si pas d'enfants
    
    #assign des enfants et lui même si pas enfants
    for task in all_tasks:
        descendant_assigns = get_descendant_assigns(task.id)
        task_assigns[task.id] = descendant_assigns
        all_assign_ids.update(descendant_assigns)
        if task.assign_id:
            all_assign_ids.add(task.assign_id)

    # Charger les users
    if all_assign_ids:
        users = {u.id: u.username for u in User.query.filter(User.id.in_(all_assign_ids)).all()}
    else:
        users = {}
    
    personnes = {}
    
    for task in all_tasks:
        # Si c'est une tâche avec des enfants
        if task.id in task_assigns and task_assigns[task.id]:
            personnes[task.id] = ", ".join(users[aid] for aid in task_assigns[task.id] if aid in users)
        # Si c'est une tâche feuille (assignée directement)
        elif task.assign_id and task.assign_id in users:
            personnes[task.id] = users[task.assign_id]
        else:
            personnes[task.id] = "Non assigné"
    
    return render_template("planning.html", planning=parent_tasks, personnes=personnes)


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
@login_required
#@admin_required TODO remettre le admin required
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


@plan_bp.route('/<int:task_id>/assign', methods=["Post"])
@login_required
def assign(task_id):
    task = Task.find_by_id(task_id)
    if task is None:
        return jsonify({"success": False, "error": "Task non trouvée"}), 404
    if User.find_by_id(g.user.id) is not None:
        task.update(assign_id=g.user.id)
        return jsonify({
            "success": True}), 200
    else:
        return jsonify({"success": False, "error": "Utilisateur non trouvée"}), 404