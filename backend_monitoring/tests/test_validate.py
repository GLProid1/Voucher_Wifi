import os, sys
import json
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.app import create_app
from app.utils import ensure_log_directory

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_store_voucher(client):
    code = "TEST123"
    response = client.post("/api/monitoring/store-voucher", json={"voucher_code": code})
    assert response.status_code == 200
    assert response.json["status"] in ["success", "exists"]

def test_validate_voucher_success(client):
    # Simpan dulu voucher
    code = "VALID123"
    client.post("/api/monitoring/store-voucher", json={"voucher_code": code})

    # Validasi voucher
    response = client.post("/api/monitoring/validate-voucher", json={"voucher_code": code})
    assert response.status_code == 200
    assert response.json["valid"] is True

def test_validate_voucher_fail(client):
    response = client.post("/api/monitoring/validate-voucher", json={"voucher_code": "XYZ999"})
    assert response.status_code == 404
    assert response.json["valid"] is False
