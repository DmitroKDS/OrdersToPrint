from flask import Blueprint

bp = Blueprint('catch_orders', __name__)

from . import routes