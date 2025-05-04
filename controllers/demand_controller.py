from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import Blueprint
from services.demand_forecast import DemandForecastService
from utils.auth_utils import role_required
demand_bp = Blueprint('demand', __name__, url_prefix='/api/demand')
@demand_bp.route('/forecast', methods=['POST'])
@jwt_required()
@role_required('supply_chain_manager')
def forecast_demand():
    user_id = get_jwt_identity()
    
    # Get sales data
    sales_df, error = DemandForecastService.get_sales_data()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Generate forecast
    forecast_results, error = DemandForecastService.forecast_7_days(sales_df, user_id)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Convert DataFrame to list of dictionaries
    forecast_data = forecast_results.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': 'Demand forecast generated successfully',
        'forecast': forecast_data
    }), 200

@demand_bp.route('/latest-forecast', methods=['GET'])
@jwt_required()
@role_required('supply_chain_manager')
def get_latest_forecast():
    # Get latest forecast
    forecast_df, error = DemandForecastService.get_latest_forecast()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Convert DataFrame to list of dictionaries
    forecast_data = forecast_df.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': 'Latest forecast retrieved successfully',
        'forecast': forecast_data
    }), 200

@demand_bp.route('/forecasts', methods=['GET'])
@jwt_required()
@role_required('supply_chain_manager')
def get_all_forecasts():
    # Get all forecasts grouped by date
    forecasts = DemandForecastService.get_all_forecast_dates()
    
    return jsonify({
        'success': True,
        'message': 'Forecast dates retrieved successfully',
        'forecasts': forecasts
    }), 200

@demand_bp.route('/delete-forecast/<date>', methods=['DELETE'])
@jwt_required()
@role_required('supply_chain_manager')
def delete_forecast(date):
    user_id = get_jwt_identity()
    
    # Delete forecast for the specified date
    success, message = DemandForecastService.delete_forecast_by_date(date, user_id)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

