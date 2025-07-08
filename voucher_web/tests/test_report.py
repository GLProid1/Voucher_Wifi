import pytest
import sys
import os
from unittest.mock import patch

# path ke app.routes
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

def test_report_success(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value = MockResponse({"status": "ok"}, 200)
        payload = {
            "mac": "AA:BB:CC:DD:EE:FF",
            "data": {
                "cpu": "Intel i5",
                "ram": "8GB"
            }
        }
        response = client.post("/report", json=payload)
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_report_failure(client):
    with patch("requests.post", side_effect=Exception("down")):
        payload = {"mac": "AA:BB:CC:DD:EE:FF", "data": {"info": "x"}}
        response = client.post("/report", json=payload)
        assert response.status_code == 500
        assert response.json["status"] == "error"

