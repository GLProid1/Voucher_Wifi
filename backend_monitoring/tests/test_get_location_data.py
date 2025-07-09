import json, os
from datetime import datetime

def test_get_location_data(client):
  log_dir = client.application.config['LOG_DIR']
  location_file = os.path.join(log_dir, 'location_log.jsonl')
  
  sample_data = {
    "latitude": "1.234",
    "longitute": "2.345",
    "accuracy": "10",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  }
  
  with open(location_file, 'w', encoding="utf-8") as f:
    f.write(json.dumps(sample_data) + "\n")
    
  response = client.get("/api/monitoring/get-location-data")
  assert response.status_code == 200
  data = response.json
  
  assert "entries" in data
  assert isinstance(data["entries"], list)
  assert data['entries'][0]['latitude'] == "1.234"
  assert "avg_accuracy" in data
  assert "best_accuracy" in data