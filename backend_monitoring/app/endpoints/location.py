from flask import Blueprint, request, jsonify
from datetime import datetime
import os, json
from ..utils import ensure_log_directory
from ..extensions import socketio

location_bp = Blueprint('location', __name__, url_prefix='/api/monitoring')

@location_bp.route('/save-location', methods=['POST'])
def save_log():
    data = request.json
    required_fields = ['latitude', 'longitude', 'accuracy']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Tambahkan timestamp jika belum ada
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_dir = ensure_log_directory()
    location_log = os.path.join(log_dir, 'location_log.jsonl')

    with open(location_log, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + "\n")
        
    socketio.emit('location_update', data)
    return jsonify({"status": "saved"}), 200

@location_bp.route('/get-location-data', methods=['GET'])
def get_location_data():
    log_dir = ensure_log_directory()
    location_log = os.path.join(log_dir, 'location_log.jsonl')

    entries = []
    today_entries = 0
    total_accuracy = 0.0
    best_accuracy = float('inf')

    try:
        with open(location_log, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                timestamp = data.get("timestamp")
                if not timestamp:
                    continue

                entries.append(data)

                # Hitung statistik
                accuracy = float(data.get("accuracy", 0))
                total_accuracy += accuracy
                best_accuracy = min(best_accuracy, accuracy)

                # Cek apakah data hari ini
                if timestamp.startswith(datetime.now().strftime("%Y-%m-%d")):
                    today_entries += 1

        avg_accuracy = total_accuracy / len(entries) if entries else 0
        result = {
            "entries": entries[::-1],  # urutan terbaru dulu
            "total_entries": len(entries),
            "today_entries": today_entries,
            "best_accuracy": round(best_accuracy, 2) if entries else 0,
            "avg_accuracy": round(avg_accuracy, 2) if entries else 0
        }
        return jsonify(result), 200

    except FileNotFoundError:
        return jsonify({
            "entries": [],
            "total_entries": 0,
            "today_entries": 0,
            "best_accuracy": 0,
            "avg_accuracy": 0
        }), 200