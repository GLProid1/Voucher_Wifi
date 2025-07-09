import os,sys
import json
import tempfile
import pytest
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with tempfile.TemporaryDirectory() as tmpdir:
        app.config['LOG_DIR'] = tmpdir
        with app.test_client() as client:
            yield client

def test_report_success(client):
    payload = {
        "mac": "AA:BB:CC:DD:EE:FF",
        "data": {
            "cpu": "Intel",
            "ram": "16GB"
        }
    }
    response = client.post("/api/monitoring/report", json=payload)
    assert response.status_code == 200
    assert response.json["status"] == "Received"

def test_report_keystroke_logging(client):
    payload = {
        "mac": "11:22:33:44:55:66",
        "data": {
            "keystroke": "abc",
            "browser": "Firefox"
        }
    }
    response = client.post("/api/monitoring/report", json=payload)
    assert response.status_code == 200
    log_dir = client.application.config['LOG_DIR']

    traffic_log = os.path.join(log_dir, 'traffic.json')
    keystrokes_log = os.path.join(log_dir, 'keystrokes.log')

    assert os.path.exists(traffic_log)
    assert os.path.exists(keystrokes_log)

    with open(keystrokes_log, 'r') as f:
        contents = f.read()
        assert "keystroke: abc" in contents
        assert "browser: Firefox" in contents
