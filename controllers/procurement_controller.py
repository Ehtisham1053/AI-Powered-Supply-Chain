from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.procurement_service import ProcurementService
from utils.auth_utils import role_required

# Define the blueprint
procurement_bp = Blueprint('procurement', __name__, url_prefix='/api/procurement')

@procurement_bp.route('/evaluate-suppliers/<int:item>', methods=['GET'])
@jwt_required()
@role_required('procurement_officer')
def evaluate_suppliers(item):
    user_id = get_jwt_identity()
    
    # Evaluate suppliers
    ranked_suppliers, error = ProcurementService.evaluate_suppliers(item, user_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Convert DataFrame to list of dictionaries
    supplier_data = ranked_suppliers.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': 'Suppliers evaluated successfully',
        'suppliers': supplier_data
    }), 200

@procurement_bp.route('/create-purchase-order', methods=['POST'])
@jwt_required()
@role_required('procurement_officer')
def create_purchase_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['supplier_id', 'items']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Create purchase order
    purchase_order, error = ProcurementService.create_purchase_order(
        supplier_id=data['supplier_id'],
        items=data['items'],
        user_id=user_id
    )
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Purchase order created successfully',
        'purchase_order': purchase_order
    }), 201

@procurement_bp.route('/purchase-orders', methods=['GET'])
@jwt_required()
@role_required(['procurement_officer', 'supply_chain_manager'])
def get_purchase_orders():
    # Get purchase orders
    purchase_orders, error = ProcurementService.get_purchase_orders()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Purchase orders retrieved successfully',
        'purchase_orders': purchase_orders
    }), 200

@procurement_bp.route('/process-purchase-order/<int:po_id>', methods=['POST'])
@jwt_required()
@role_required(['procurement_officer', 'supplier'])
def process_purchase_order(po_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    data = request.get_json()
    
    # Validate required fields
    if 'action' not in data:
        return jsonify({'success': False, 'message': 'Missing required field: action'}), 400
    
    # For supplier role, only allow accept/reject actions
    if claims.get('role') == 'supplier' and data['action'] not in ['accept', 'reject']:
        return jsonify({'success': False, 'message': 'Invalid action for supplier role'}), 403
    
    # Process purchase order
    success, message = ProcurementService.process_purchase_order(
        po_id=po_id,
        action=data['action'],
        user_id=user_id
    )
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

@procurement_bp.route('/blacklist-supplier/<int:supplier_id>', methods=['POST'])
@jwt_required()
@role_required('procurement_officer')
def blacklist_supplier(supplier_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if 'blacklist' not in data:
        return jsonify({'success': False, 'message': 'Missing required field: blacklist'}), 400
    
    # Blacklist supplier
    success, message = ProcurementService.blacklist_supplier(
        supplier_id=supplier_id,
        blacklist=data['blacklist'],
        user_id=user_id
    )
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400




@procurement_bp.route('/warehouse-requests', methods=['GET'])
@jwt_required()
@role_required('procurement_officer')
def get_pending_warehouse_requests():
    requests, error = ProcurementService.get_warehouse_requests()
    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'message': 'Pending warehouse requests fetched successfully',
        'requests': requests
    }), 200




@procurement_bp.route('/select-supplier', methods=['POST'])
@jwt_required()
@role_required('procurement_officer')
def select_supplier():
    user_id = get_jwt_identity()
    data = request.get_json()

    if 'supplier_id' not in data or 'item' not in data:
        return jsonify({'success': False, 'message': 'Missing supplier_id or item'}), 400

    result, error = ProcurementService.select_supplier_for_item(
        supplier_id=data['supplier_id'],
        item=data['item'],
        user_id=user_id
    )

    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'selected_supplier': result}), 200



@procurement_bp.route('/remove-supplier/<int:item>', methods=['DELETE'])
@jwt_required()
@role_required('procurement_officer')
def remove_selected_supplier(item):
    user_id = get_jwt_identity()
    success, message = ProcurementService.remove_selected_supplier(item, user_id)

    return jsonify({'success': success, 'message': message}), (200 if success else 400)



@procurement_bp.route('/po-generation-data', methods=['GET'])
@jwt_required()
@role_required('procurement_officer')
def get_po_generation_data():
    with_suppliers, without_suppliers, error = ProcurementService.get_po_generation_data()
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({
        'success': True,
        'with_suppliers': with_suppliers,
        'without_suppliers': without_suppliers
    }), 200



@procurement_bp.route('/confirm-po', methods=['POST'])
@jwt_required()
@role_required('procurement_officer')
def confirm_po():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not all(k in data for k in ('item', 'supplier_id')):
        return jsonify({'success': False, 'message': 'Missing item or supplier_id'}), 400

    confirmed, error = ProcurementService.confirm_purchase_order(
        item=data['item'],
        supplier_id=data['supplier_id'],
        user_id=user_id
    )
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'confirmed_po': confirmed}), 200
