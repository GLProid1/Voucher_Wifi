from flask import Blueprint, request, jsonify, current_app
import os
from ..utils import ensure_log_directory

validate_bp = Blueprint('validate', __name__, url_prefix='/api/monitoring')

@validate_bp.route('/validate-voucher', methods=['POST'])
def validate_voucher():
    try:
        data = request.get_json()
        current_app.logger.info(f"DATA MASUK: {data}")  # ✅ Log data untuk debug

        if not data or 'voucher_code' not in data:
            return jsonify({'valid': False, 'message': 'Invalid input'}), 400

        code = data.get('voucher_code', '').strip().upper()
        if not code:
            return jsonify({'valid': False, 'message': 'Invalid voucher code'}), 400

        log_dir = ensure_log_directory()
        voucher_path = os.path.join(log_dir, 'voucher_codes.txt')

        if not os.path.exists(voucher_path):
            return jsonify({'valid': False, 'message': 'Voucher file not found'}), 404

        with open(voucher_path, 'r') as f:
            vouchers = [v.strip().upper() for v in f.readlines() if v.strip()]

        current_app.logger.info(f"VOUCHERS TERSEDIA: {vouchers}")  # ✅ Log list voucher

        if code not in vouchers:
            return jsonify({'valid': False, 'message': 'Voucher code not found'}), 404

        vouchers.remove(code)
        with open(voucher_path, 'w') as f:
            f.writelines(v + '\n' for v in vouchers)

        return jsonify({'valid': True, 'message': 'Voucher code is valid and has been used'}), 200

    except Exception as e:
        current_app.logger.exception("Exception saat validasi voucher")  # ✅ Log exception lengkap
        return jsonify({'valid': False, 'message': str(e)}), 500
    
@validate_bp.route('/store-voucher', methods=['POST'])
def store_voucher():
        try:
            data = request.get_json()
            code = data.get('voucher_code', '').strip().upper()
            if not code:
                return jsonify({'status': 'error', 'message': 'Voucher kosong'}), 400
            
            log_dir = ensure_log_directory()
            voucher_path = os.path.join(log_dir, 'voucher_codes.txt')
            
            with open(voucher_path, 'a') as f:
                f.write(code + '\n')
                
            current_app.logger.info(f"Voucher disimpan: {code}")  # ✅ Log voucher yang disimpan
            return jsonify({'status': 'success', 'message': 'Voucher disimpan'}), 200
        except Exception as e:
            current_app.logger.exception("Error saat menyimpan voucher")
            return jsonify({'status': 'error', 'message': str(e)}), 500