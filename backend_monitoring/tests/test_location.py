import os
import sys
import json
import pytest
from flask import Flask

# Tambahkan path app agar modul bisa diimpor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_save_location_success(client):
    payload = {
        "latitude": "-6.200000",
        "longitude": "106.816666",
        "accuracy": "5"
    }
    response = client.post("/api/monitoring/save-location", json=payload)
    assert response.status_code == 200
    assert response.json["status"] == "saved"

def test_save_location_missing_field(client):
    payload = {
        "latitude": "-6.200000"
    }
    response = client.post("/api/monitoring/save-location", json=payload)
    assert response.status_code == 400
    assert "error" in response.json

def test_get_location_data(client):
    response = client.get("/api/monitoring/get-location-data")
    assert response.status_code == 200
    assert "entries" in response.json
    assert "total_entries" in response.json
