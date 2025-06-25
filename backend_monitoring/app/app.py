from flask import Flask
from .extensions import socketio
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key_for_socketio'

    from .endpoints.report import report_bp
    from .endpoints.location import location_bp
    from .endpoints.validate import validate_bp
    from .endpoints.ui import ui_bp
    from .endpoints.network import network_bp
    

    app.register_blueprint(ui_bp)
    app.register_blueprint(network_bp, url_prefix="/api/monitoring")
    app.register_blueprint(report_bp, url_prefix="/api/monitoring")
    app.register_blueprint(location_bp, url_prefix="/api/monitoring")
    app.register_blueprint(validate_bp, url_prefix="/api/monitoring")

    socketio.init_app(app)
    return app
