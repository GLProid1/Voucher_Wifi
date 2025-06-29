from flask import Blueprint, request, jsonify
import routeros_api

network_bp = Blueprint('network', __name__)

MIKROTIK_IP = '10.10.2.1'
MIKROTIK_USERNAME = 'admin'
MIKROTIK_PASSWORD = 'PBL08'

def get_mikrotik_api():
  connection = routeros_api.RouterOsApiPool(
    host=MIKROTIK_IP,
    username=MIKROTIK_USERNAME,
    password=MIKROTIK_PASSWORD,
    port=8728,
    plaintext_login=True,
  )
  return connection.get_api()

@network_bp.route('/unlock-internet', methods=['POST'])
def unlock_internet():
  try:
    mac = request.json.get('mac')
    if not mac:
      return jsonify({"status": "error", "message": "MAC address is required"}), 400
    
    api = get_mikrotik_api()
    ip_binding = api.get_resource('/ip/hotspot/ip-binding')
    ip_binding.add(mac_address=mac, type='bypassed')
    
    return jsonify({"status": "success", "message": "Internet unlocked for MAC address", "mac": mac}), 200
  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500
  
@network_bp.route('/lock-internet', methods=['POST'])
def lock_internet():
  try:
    mac = request.json.get('mac')
    if not mac:
      return jsonify({"status": "error", "message": "MAC address is required"}), 400
    
    api = get_mikrotik_api()
    ip_binding = api.get_resource('/ip/hotspot/ip-binding')
    existing = ip_binding.get(mac_address=mac)
    for entry in existing:
      ip_binding.remove(id=entry['.id'])
    
    return jsonify({"status": "success", "message": "Internet locked for MAC address", "mac": mac}), 200
  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500