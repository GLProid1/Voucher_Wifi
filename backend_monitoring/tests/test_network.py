import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

@patch("app.endpoints.network.get_mikrotik_api")
def test_unlock_internet(mock_mikrotik, client):
    mock_binding = MagicMock()
    mock_mikrotik.return_value.get_resource.return_value = mock_binding

    response = client.post("/api/monitoring/unlock-internet", json={
        "mac": "AA:BB:CC:DD:EE:FF"
    }, environ_base={"REMOTE_ADDR": "10.10.1.100"})

    assert response.status_code == 200
    assert response.json["status"] == "success"
    mock_binding.add.assert_called_once()

@patch("app.endpoints.network.get_mikrotik_api")
def test_lock_internet(mock_mikrotik, client):
    mock_binding = MagicMock()
    mock_binding.get.return_value = [{'.id': 'abc123'}]
    mock_mikrotik.return_value.get_resource.return_value = mock_binding

    response = client.post("/api/monitoring/lock-internet", json={
        "mac": "AA:BB:CC:DD:EE:FF"
    })

    assert response.status_code == 200
    assert response.json["status"] == "success"
    mock_binding.remove.assert_called_once_with(id='abc123')
