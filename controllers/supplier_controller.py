from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.supplier_service import SupplierService
from utils.auth_utils import role_required

# Define blueprint
supplier_bp = Blueprint('supplier', __name__, url_prefix='/api/supplier')

@supplier_bp.route('/add', methods=['POST'])
@jwt_required()
@role_required('procurement_officer')
def add_supplier():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = [
        'supplier_id', 'on_time_delivery_rate', 'order_accuracy_rate', 'lead_time',
        'fulfillment_rate', 'defect_rate', 'return_rate', 'unit_price',
        'responsiveness_score', 'flexibility_rating', 'years_in_business',
        'customer_satisfaction_rating'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Add supplier
    success, message = SupplierService.add_supplier(data, user_id)
    
    if success:
        return jsonify({'success': True, 'message': message}), 201
    else:
        return jsonify({'success': False, 'message': message}), 400

@supplier_bp.route('/all', methods=['GET'])
@jwt_required()
@role_required(['procurement_officer', 'supply_chain_manager'])
def get_all_suppliers():
    # Get all suppliers
    suppliers, error = SupplierService.get_suppliers(include_blacklisted=True)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Suppliers retrieved successfully',
        'suppliers': suppliers
    }), 200

@supplier_bp.route('/active', methods=['GET'])
@jwt_required()
@role_required(['procurement_officer', 'supply_chain_manager'])
def get_active_suppliers():
    # Get active (non-blacklisted) suppliers
    suppliers, error = SupplierService.get_suppliers(include_blacklisted=False)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Active suppliers retrieved successfully',
        'suppliers': suppliers
    }), 200

@supplier_bp.route('/<int:supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    # Get supplier by ID
    supplier, error = SupplierService.get_supplier_by_id(supplier_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 404
    
    return jsonify({
        'success': True,
        'message': 'Supplier retrieved successfully',
        'supplier': supplier
    }), 200

@supplier_bp.route('/purchase-orders', methods=['GET'])
@jwt_required()
@role_required('supplier')
def get_supplier_purchase_orders():
    claims = get_jwt()
    supplier_id = claims.get('supplier_id')
    
    if not supplier_id:
        return jsonify({'success': False, 'message': 'Supplier ID not found in token'}), 400
    
    # Get purchase orders for this supplier
    purchase_orders, error = SupplierService.get_supplier_purchase_orders(supplier_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Purchase orders retrieved successfully',
        'purchase_orders': purchase_orders
    }), 200

@supplier_bp.route('/update/<int:supplier_id>', methods=['PUT'])
@jwt_required()
@role_required('procurement_officer')
def update_supplier(supplier_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Update supplier
    success, message = SupplierService.update_supplier(supplier_id, data, user_id)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400