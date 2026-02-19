from flask import Blueprint

ressources_bp = Blueprint("ressources", __name__, url_prefix="/ressources", template_folder="templates")

from . import routes  # noqa: F401, E402