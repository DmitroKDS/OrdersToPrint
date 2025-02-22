from flask import Blueprint

bp = Blueprint('generate_canvas', __name__)

from . import routes