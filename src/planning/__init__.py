from flask import Blueprint

plan_bp = Blueprint("planning", __name__, url_prefix="/tasks", template_folder="templates")

from . import routes  # noqa: F401, E402