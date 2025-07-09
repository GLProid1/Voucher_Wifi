import os, json

def test_store_voucher_success(client):
  response = client.post("/api/monitoring/store-voucher", json={"voucher_code": "TEST123"})
  assert response.status_code == 200
  assert response.json["status"] == "success"
  
  log_dir = client.application.config['LOG_DIR']
  file_path = os.path.join(log_dir, 'voucher_codes.txt')
  assert os.path.exists(file_path)
  
  with open(file_path, 'r') as f:
    line = f.readline().strip()
    assert "TEST123" in line
    
def test_store_voucher_duplicate(client):
  client.post("/api/monitoring/store-voucher", json={"voucher_code": "DUPLICATE123"})
  response = client.post("/api/monitoring/store-voucher", json={"voucher_code": "DUPLICATE123"})
  assert response.status_code == 200
  assert response.json["status"] == "exists"
  
def test_store_voucher_empty(client):
  response = client.post("/api/monitoring/store-voucher", json={"voucher_code": ""})
  assert response.status_code == 400
  assert response.json["status"] == "error"