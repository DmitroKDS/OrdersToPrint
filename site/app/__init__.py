import logging.handlers
from flask import Flask
import logging
import sys

def create_app() -> Flask:
    """
    This function create app and register all blueprints
    And return fully configured app
    """

    # Create Flask app instance

    app = Flask(__name__, template_folder=f"{sys._MEIPASS}/app/templates" if getattr(sys, 'frozen', False) else "templates")

    # Logger

    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    file_handler = logging.handlers.RotatingFileHandler(
        "app.log", maxBytes=1024 * 1024 * 5, backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_formatter)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


    # Register blueprints

    from .code.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .code.catch_orders import bp as catch_orders_bp
    app.register_blueprint(catch_orders_bp, url_prefix = "/catch_orders")

    from .code.generate_canvas import bp as generate_canvas_bp
    app.register_blueprint(generate_canvas_bp, url_prefix = "/generate_canvas")

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application</h1>'

    return app