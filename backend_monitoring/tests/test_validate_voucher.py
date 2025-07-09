import os, sys

def test_validate_voucher_success(client):
  log_dir = client.application.config['LOG_DIR']
  voucher_path = os.path.join(log_dir, 'voucher_codes.txt')
  
  with open(voucher_path, 'w') as f:
    f.write("VALID123\n")
    
  response = client.post("/api/monitoring/validate-voucher", json={"voucher_code": "VALID123"})
  assert response.status_code == 200