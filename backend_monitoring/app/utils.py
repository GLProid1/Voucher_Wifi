# app/utils.py
from flask import current_app
import os

def ensure_log_directory():
    log_dir = current_app.config.get("LOG_DIR", os.path.join(os.path.dirname(__file__), "logs"))
    os.makedirs(log_dir, exist_ok=True)
    return log_dir
