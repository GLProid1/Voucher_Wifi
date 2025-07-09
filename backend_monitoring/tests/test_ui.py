import os, json

def test_ui_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Monitoring Dashboard" in response.data
    
def test_ui_log_monitoring(client):
    log_path = os.path.join(client.application.config['LOG_DIR'], "traffic.json")
    sample = {'mac': 'AA:BB:CC:DD:EE:FF', "timestamp": "2025-07-09 12:00:00"}
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(sample) + "\n")
    response = client.get("/log_monitor")  # ✅ perbaikan path
    assert response.status_code == 200
    assert b"AA:BB:CC:DD:EE:FF" in response.data

def test_ui_key_logger(client):
    log_path = os.path.join(client.application.config['LOG_DIR'], "keystrokes.log")
    content = "[Timestamp: 2025-07-09]\nkeystroke: abc\nbrowser: Chrome\n\n"

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(content)

    response = client.get("/key_logger")
    assert response.status_code == 200
    assert b"keystroke: abc" in response.data

def test_ui_activity_monitoring(client):
    log_path = os.path.join(client.application.config['LOG_DIR'], "traffic.json")
    sample = {
      'timestamp': '2025-07-09 12:00:00',
      'hostname': 'test-host',
      'ip_address': '192.169.2.1',
      'os': 'Linux',
      'os_version': 'Ubuntu 20.04',
      'activity': 'Test activity',
      'browser_history': [
        {'url': 'http://example.com'},
        {'url': 'http://example.org'}
      ]
    }
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(sample) + "\n")

    response = client.get("/activity_monitor")
    assert response.status_code == 200
    # Jika HTML template menampilkan "Test activity", maka aktifkan ini:
    assert b"Test activity" in response.data


def test_ui_maps(client):
    response = client.get("/maps")
    assert response.status_code == 200
    assert b"<html" in response.data
