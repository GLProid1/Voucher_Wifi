from flask import Flask
from app.extensions import socketio

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key_for_socketio'

    from app.endpoints.report import report_bp
    from app.endpoints.location import location_bp
    from app.endpoints.validate import validate_bp
    from app.endpoints.ui import ui_bp
    from app.endpoints.network import network_bp
    

    app.register_blueprint(ui_bp)
    app.register_blueprint(network_bp, url_prefix="/api/monitoring")
    app.register_blueprint(report_bp, url_prefix="/api/monitoring")
    app.register_blueprint(location_bp, url_prefix="/api/monitoring")
    app.register_blueprint(validate_bp, url_prefix="/api/monitoring")

    socketio.init_app(app)
    return app
