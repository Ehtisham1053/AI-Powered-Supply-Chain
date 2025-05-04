from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.warehouse_service import WarehouseService
from utils.auth_utils import role_required

# Define blueprint
warehouse_bp = Blueprint('warehouse', __name__, url_prefix='/api/warehouse')

@warehouse_bp.route('/data', methods=['GET'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team'])
def get_warehouse_data():
    # Get warehouse data
    warehouse_df, error = WarehouseService.get_warehouse_data()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Convert DataFrame to list of dictionaries
    warehouse_data = warehouse_df.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': 'Warehouse data retrieved successfully',
        'warehouse': warehouse_data
    }), 200

@warehouse_bp.route('/add', methods=['POST'])
@jwt_required()
@role_required('warehouse_team')
def add_warehouse_stock():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['item', 'stock']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Add warehouse stock
    success, message = WarehouseService.add_warehouse_stock(
        item=data['item'],
        stock=data['stock'],
        user_id=user_id
    )
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

@warehouse_bp.route('/optimize', methods=['POST'])
@jwt_required()
@role_required('warehouse_team')
def optimize_warehouse():
    user_id = get_jwt_identity()
    
    # Optimize warehouse
    success, message = WarehouseService.optimize_warehouse(user_id)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

@warehouse_bp.route('/process-request/<int:request_id>', methods=['POST'])
@jwt_required()
@role_required('warehouse_team')
def process_inventory_request(request_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if 'approve' not in data:
        return jsonify({'success': False, 'message': 'Missing required field: approve'}), 400
    
    # Process inventory request
    success, message = WarehouseService.process_inventory_request(
        request_id=request_id,
        approve=data['approve'],
        user_id=user_id
    )
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

@warehouse_bp.route('/requests', methods=['GET'])
@jwt_required()
@role_required(['warehouse_team', 'procurement_officer'])
def get_warehouse_requests():
    # Get warehouse requests
    requests, error = WarehouseService.get_warehouse_requests()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Warehouse requests retrieved successfully',
        'requests': requests
    }), 200

@warehouse_bp.route('/forecast', methods=['GET'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team'])
def get_30day_forecast():
    # Get 30-day forecast
    forecast_results, error = WarehouseService.forecast_30_days()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Convert DataFrame to list of dictionaries
    forecast_data = forecast_results.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': '30-day forecast retrieved successfully',
        'forecast': forecast_data
    }), 200