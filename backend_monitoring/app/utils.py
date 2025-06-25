import os

def ensure_log_directory():
  log_dir = os.path.join(os.path.dirname(__file__), 'logs')
  os.makedirs(log_dir, exist_ok=True)
  return log_dir