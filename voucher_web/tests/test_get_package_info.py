import pytest
import sys
import os

# setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.routes import main_bp
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test"
    app.register_blueprint(main_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_package_info_basic(client):
    response = client.get("/get-package-info?service=basic")
    assert response.status_code == 200
    assert response.json["name"] == "Standar"
    assert response.json["duration"] == "1 Jam"

def test_get_package_info_premium(client):
    response = client.get("/get-package-info?service=premium")
    assert response.status_code == 200
    assert response.json["name"] == "Premium"
    assert response.json["duration"] == "2 Jam"

def test_get_package_info_default(client):
    response = client.get("/get-package-info")
    assert response.status_code == 200
    assert response.json["name"] == "Standar"

