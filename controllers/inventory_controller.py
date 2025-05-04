from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import Blueprint
from services.inventory_service import InventoryService
from utils.auth_utils import role_required

# Correct blueprint declaration
inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

@inventory_bp.route('/data', methods=['GET'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team', 'sales_officer'])
def get_inventory_data():
    """Get all inventory data"""
    # Get inventory data
    inventory_df, error = InventoryService.get_inventory_data()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Convert DataFrame to list of dictionaries
    inventory_data = inventory_df.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': 'Inventory data retrieved successfully',
        'inventory': inventory_data
    }), 200

@inventory_bp.route('/store/<int:store_id>', methods=['GET'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team', 'sales_officer'])
def get_store_inventory(store_id):
    """Get inventory data for a specific store"""
    # Get inventory data
    inventory_df, error = InventoryService.get_inventory_data()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Filter by store
    store_inventory = inventory_df[inventory_df['Store'] == store_id]
    
    # Convert DataFrame to list of dictionaries
    inventory_data = store_inventory.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': f'Inventory data for store {store_id} retrieved successfully',
        'inventory': inventory_data
    }), 200

@inventory_bp.route('/item/<int:item_id>', methods=['GET'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team', 'sales_officer'])
def get_item_inventory(item_id):
    """Get inventory data for a specific item across all stores"""
    # Get inventory data
    inventory_df, error = InventoryService.get_inventory_data()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Filter by item
    item_inventory = inventory_df[inventory_df['Item'] == item_id]
    
    # Convert DataFrame to list of dictionaries
    inventory_data = item_inventory.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': f'Inventory data for item {item_id} retrieved successfully',
        'inventory': inventory_data
    }), 200

@inventory_bp.route('/add', methods=['POST'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team'])
def add_inventory():
    """Add or update inventory for a specific store and item"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['store', 'item', 'stock']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Add inventory
    success, message = InventoryService.add_inventory(
        store=data['store'],
        item=data['item'],
        stock=data['stock'],
        user_id=user_id
    )
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

@inventory_bp.route('/update/<int:store_id>/<int:item_id>', methods=['PUT'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team'])
def update_inventory(store_id, item_id):
    """Update inventory for a specific store and item"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if 'stock' not in data:
        return jsonify({'success': False, 'message': 'Missing required field: stock'}), 400
    
    # Update inventory (set absolute value, not increment)
    success, message = InventoryService.update_inventory(
        store=store_id,
        item=item_id,
        stock=data['stock'],
        user_id=user_id
    )
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

@inventory_bp.route('/optimize', methods=['POST'])
@jwt_required()
@role_required('supply_chain_manager')
def optimize_inventory():
    """Optimize inventory based on 7-day forecast"""
    user_id = get_jwt_identity()
    
    # Optimize inventory
    success, message = InventoryService.optimize_inventory(user_id)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

@inventory_bp.route('/requests', methods=['GET'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team'])
def get_inventory_requests():
    """Get all pending inventory requests"""
    # Get inventory requests
    requests, error = InventoryService.get_inventory_requests()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Inventory requests retrieved successfully',
        'requests': requests
    }), 200

@inventory_bp.route('/low-stock', methods=['GET'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team'])
def get_low_stock_items():
    """Get items with low stock (below threshold)"""
    # Get threshold from query parameters (default: 20)
    threshold = request.args.get('threshold', 20, type=int)
    
    # Get low stock items
    low_stock_items, error = InventoryService.get_low_stock_items(threshold)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Low stock items retrieved successfully',
        'items': low_stock_items
    }), 200

@inventory_bp.route('/bulk-update', methods=['POST'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team'])
def bulk_update_inventory():
    """Update inventory for multiple items at once"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if 'items' not in data or not isinstance(data['items'], list):
        return jsonify({'success': False, 'message': 'Missing or invalid items array'}), 400
    
    # Validate each item
    for item in data['items']:
        required_fields = ['store', 'item', 'stock']
        for field in required_fields:
            if field not in item:
                return jsonify({'success': False, 'message': f'Missing required field in item: {field}'}), 400
    
    # Update inventory
    success, message, results = InventoryService.bulk_update_inventory(
        items=data['items'],
        user_id=user_id
    )
    
    if success:
        return jsonify({
            'success': True, 
            'message': message,
            'results': results
        }), 200
    else:
        return jsonify({'success': False, 'message': message}), 400