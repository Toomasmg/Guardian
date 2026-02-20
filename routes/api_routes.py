from flask import Blueprint, request, jsonify
from models import License
from database import db, limiter
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/validate_license', methods=['POST'])
@limiter.limit("5 per minute")
def validate_license():
    try:
        if not request.is_json:
            return jsonify({"valid": False, "message": "JSON requerido"}), 400

        data = request.get_json()
        api_key = data.get('api_key')
        hwid = data.get('hardware_id')

        if not api_key:
            return jsonify({"valid": False, "message": "Falta API Key"}), 400
        
        if not hwid:
            return jsonify({"valid": False, "message": "Falta Hardware ID (Seguridad)"}), 400

        lic = License.query.filter_by(api_key=api_key).first()
        
        if not lic:
            return jsonify({"valid": False, "message": "Licencia inválida"}), 401
            
        if not lic.is_active:
            return jsonify({"valid": False, "message": "Licencia suspendida por falta de pago"}), 403
            
        if datetime.now() > lic.expiration_date:
            return jsonify({"valid": False, "message": "Licencia vencida"}), 403

        if lic.hardware_id is None:
            lic.hardware_id = hwid
            db.session.commit()
        elif lic.hardware_id != hwid:
            return jsonify({
                "valid": False, 
                "message": "Violación de seguridad: Licencia ya usada en otra PC."
            }), 403
            
        days = (lic.expiration_date - datetime.now()).days
        return jsonify({
            "valid": True, 
            "days_left": days,
            "owner": lic.owner_name
        }), 200

    except Exception as e:
        print(f"Error API: {e}")
        return jsonify({"valid": False, "message": "Error interno del servidor"}), 500