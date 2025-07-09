# tests/conftest.py
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app

@pytest.fixture
def client():
    temp_dir = tempfile.TemporaryDirectory()
    app = create_app()
    app.config['TESTING'] = True
    app.config['LOG_DIR'] = temp_dir.name  # 👈 override lokasi log

    with app.test_client() as client:
        yield client
