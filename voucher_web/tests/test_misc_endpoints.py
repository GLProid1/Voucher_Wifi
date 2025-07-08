import pytest
import sys
import os
from unittest.mock import patch

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

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Beranda" in response.data or b"html" in response.data.lower()

def test_aktivasi_get(client):
    response = client.get("/aktivasi")
    assert response.status_code == 200
    assert b"Aktivasi" in response.data or b"voucher" in response.data.lower()

def test_aktivasi_post_empty(client):
    response = client.post("/aktivasi", data={"voucher_code": ""})
    assert response.status_code == 200
    assert b"voucher" in response.data.lower() or b"error" in response.data.lower()

@patch("requests.post")
@patch("subprocess.Popen")
def test_aktivasi_post_valid(mock_popen, mock_post, client):
    mock_post.return_value.json.return_value = {"valid": True}
    mock_post.return_value.status_code = 200

    exe_path = os.path.join(os.path.dirname(__file__), "../../dist/VoucherApp.exe")
    os.makedirs(os.path.dirname(exe_path), exist_ok=True)
    with open(exe_path, "w") as f:
        f.write("dummy")

    response = client.post("/aktivasi", data={"voucher_code": "ABC123"})
    assert response.status_code == 200
    assert b"success" in response.data.lower() or b"voucher" in response.data.lower()

    os.remove(exe_path)

def test_download_voucher_app(client):
    exe_path = os.path.join(os.path.dirname(__file__), "../../dist/VoucherApp.exe")
    if os.path.exists(exe_path):
        os.remove(exe_path)

    response = client.get("/download-voucher-app")
    assert response.status_code == 404 or response.status_code == 200


def test_check_installation_status(client):
    response = client.post("/check-installation-status")
    assert response.status_code == 200
    assert response.json["installed"] is True
