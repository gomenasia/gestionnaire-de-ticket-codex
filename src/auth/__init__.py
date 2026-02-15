from flask import Blueprint

from src.auth.utils import load_logged_in_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

auth_bp.before_app_request(load_logged_in_user)

from . import routes  # noqa: F401, E402
