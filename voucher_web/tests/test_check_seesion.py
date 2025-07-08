import pytest
import sys
import os
from unittest.mock import patch

# Tambahkan path agar app bisa diimpor
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

@patch("requests.get")
def test_check_session_active(mock_get, client):
    with client.session_transaction() as sess:
        sess["mac_address"] = "00:11:22:33:44:55"

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"active": True}

    response = client.get("/check-session")
    assert response.status_code == 200
    assert response.json["active"] is True

@patch("requests.get")
def test_check_session_inactive(mock_get, client):
    with client.session_transaction() as sess:
        sess["mac_address"] = "00:11:22:33:44:55"
        
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"active": False}

    response = client.get("/check-session")
    assert response.status_code == 200
    assert response.json["active"] is False

def test_check_session_no_mac(client):
    response = client.get("/check-session")
    assert response.status_code == 200
    assert response.json["active"] is False
