import pytest
import sys
import os
from unittest.mock import patch

# setup path import
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

def test_save_location_success(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value = MockResponse({"saved": True}, 200)
        response = client.post("/save-location", json={"latitude": "1.1", "longitude": "2.2"})
        assert response.status_code == 200
        assert "saved" in response.json

def test_result_redirect(client):
    response = client.post("/result", data={
        "latitude": "1.0",
        "longitude": "2.0",
        "accuracy": "5",
        "service": "basic",
        "mac": "00:11:22:33:44:55"
    })
    assert response.status_code in [302, 308]  # redirect ke /aktivasi
