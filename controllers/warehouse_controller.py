from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.warehouse_service import WarehouseService
from utils.auth_utils import role_required
from models.warehouse import Forecasted30Days
# Define blueprint
warehouse_bp = Blueprint('warehouse', __name__, url_prefix='/api/warehouse')

@warehouse_bp.route('/data', methods=['GET'])
@jwt_required()
@role_required(['supply_chain_manager', 'warehouse_team'])
def get_warehouse_data():
    warehouse_df, error = WarehouseService.get_warehouse_data()
    if error:
        return jsonify({'success': False, 'message': error}), 400

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

    required_fields = ['item', 'stock']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

    success, message = WarehouseService.add_warehouse_stock(
        item=data['item'],
        stock=data['stock'],
        user_id=user_id
    )

    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400



@warehouse_bp.route('/process-request/<int:request_id>', methods=['POST'])
@jwt_required()
@role_required(['warehouse_team', 'procurement_officer'])
def process_inventory_request(request_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if 'approve' not in data:
        return jsonify({'success': False, 'message': 'Missing required field: approve'}), 400

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
    forecast_results = Forecasted30Days.query.all()

    if not forecast_results:
        return jsonify({'success': False, 'message': 'No forecast data found'}), 404

    forecast_data = [
        {
            "item": row.item,
            "total_predicted_sales": row.total_predicted_sales,
            "forecast_date": row.forecast_date.strftime("%Y-%m-%d")
        } for row in forecast_results
    ]

    return jsonify({
        'success': True,
        'message': '30-day forecast retrieved successfully',
        'forecast': forecast_data
    }), 200

@warehouse_bp.route('/forecast/generate', methods=['POST'])
@jwt_required()
@role_required(['warehouse_team'])
def generate_forecast():
    user_id = get_jwt_identity()
    forecast_data, error = WarehouseService.forecast_30_days(user_id=user_id)

    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'message': '30-day forecast generated and saved successfully',
        'forecast': forecast_data  # Optional: useful if you want to show instantly
    }), 200





@warehouse_bp.route('/optimize/status', methods=['GET'])
@jwt_required()
@role_required(['warehouse_team'])
def get_optimization_status():
    data, error = WarehouseService.get_optimization_status()
    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'message': 'Warehouse optimization status fetched successfully',
        'items': data
    }), 200



@warehouse_bp.route('/optimize', methods=['POST'])
@jwt_required()
@role_required(['warehouse_team'])
def optimize_warehouse():
    user_id = get_jwt_identity()
    success, message = WarehouseService.optimize_warehouse(user_id)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 500
