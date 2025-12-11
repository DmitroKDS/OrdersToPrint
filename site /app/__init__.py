from flask import Flask

import logging
from logging.handlers import RotatingFileHandler

import sys

def create_app() -> Flask:
    """
    This function create app and register all blueprints
    And return fully configured app
    """
    
    # Create Flask app instance

    app = Flask(__name__, template_folder=f"{sys._MEIPASS}/app/templates" if getattr(sys, 'frozen', False) else "templates")

    # Logger

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    fh = RotatingFileHandler(
        filename="app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(ch)


    # Register blueprints

    from .code.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .code.catch_orders import bp as catch_orders_bp
    app.register_blueprint(catch_orders_bp, url_prefix = "/catch_orders")

    # from .code.generate_canvas import bp as generate_canvas_bp
    # app.register_blueprint(generate_canvas_bp, url_prefix = "/generate_canvas")

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application</h1>'

    return app