from flask import Blueprint, request, jsonify
import os, subprocess

network_bp = Blueprint('network', __name__)

@network_bp.route('/unlock-internet', methods=['POST'])
def unlock_internet():
  ip = request.remote_addr
  try:
    subprocess.run(["iptables", "-I", "FORWARD", "-s", ip, "-j", "ACCEPT"], check=True)
    subprocess.run(["iptables", "-t", "nat" "-I", "POSTROUTING", "-s", ip, "-j", "MASQUERADE"], check=True)
    return jsonify({"status": "success", "message": "Internet unlocked", "ip": ip}), 200
  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500 
  
@network_bp.route('/lock-internet', methods=['POST'])
def lock_internet():
  ip = request.remote_addr
  try:
    subprocess.run(["iptables", "-D", "FORWARD", "-s", ip, "-j", "ACCEPT"], check=True)
    subprocess.run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-s", ip, "-j", "MASQUERADE"], check=True)
    return jsonify({"status": "success", "message": "Internet locked", "ip": ip}), 200
  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500