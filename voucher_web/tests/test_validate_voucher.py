import pytest
import sys
import os
from unittest.mock import patch

# pastikan path import ke app.routes ditemukan
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

class MockResponse:
    def __init__(self, json_data, status_code):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    @property
    def text(self):
        import json
        return json.dumps(self._json_data)

def test_validate_voucher_success(client):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = [
            MockResponse({"status": "success"}, 200),
            MockResponse({"valid": True}, 200),
            MockResponse({"status": "success"}, 200),
        ]
        response = client.post("/validate-voucher", json={"voucher_code": "ABC123", "mac": "00:11:22:33:44:55"})
        assert response.status_code == 200
        assert response.json["valid"] is True

def test_validate_voucher_invalid(client):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = [
            MockResponse({"status": "success"}, 200),
            MockResponse({"valid": False, "message": "Voucher tidak valid"}, 200),
        ]
        response = client.post("/validate-voucher", json={"voucher_code": "INVALID", "mac": "00:11:22:33:44:55"})
        assert response.status_code == 200
        assert response.json["valid"] is False

def test_validate_voucher_error(client):
    with patch("requests.post", side_effect=Exception("Server error")):
        response = client.post("/validate-voucher", json={"voucher_code": "ERROR", "mac": "00:11:22:33:44:55"})
        assert response.status_code == 500
        assert response.json["valid"] is False
