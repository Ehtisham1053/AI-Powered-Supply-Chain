from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from services.supplier_dashboard_service import SupplierDashboardService

supplier_dashboard_bp = Blueprint('supplier_dashboard', __name__, url_prefix='/api/supplier/dashboard-pos')

@supplier_dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_dashboard_pos():
    claims = get_jwt()
    supplier_id = claims.get('supplier_id')
    if not supplier_id:
        return jsonify({'success': False, 'message': 'Supplier ID missing'}), 400

    pos, error = SupplierDashboardService.get_supplier_confirmed_pos(supplier_id)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({'success': True, 'pos': pos}), 200

@supplier_dashboard_bp.route('/<int:po_id>', methods=['POST'])
@jwt_required()
def process_dashboard_po(po_id):
    claims = get_jwt()
    supplier_id = claims.get('supplier_id')
    data = request.get_json()
    action = data.get('action')

    if action not in ['confirm', 'reject']:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400

    success, message = SupplierDashboardService.process_po(supplier_id, po_id, action)
    return jsonify({'success': success, 'message': message}), 200 if success else 400
