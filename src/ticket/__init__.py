from flask import Blueprint

ticket_bp = Blueprint("ticket", __name__, url_prefix="/ticket", template_folder="templates")

from . import routes  # noqa: F401, E402