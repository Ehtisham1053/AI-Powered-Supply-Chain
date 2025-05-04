from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.sales_service import SalesService
from utils.auth_utils import role_required

# Define blueprint
sales_bp = Blueprint('sales', __name__, url_prefix='/api/sales')

@sales_bp.route('/data', methods=['GET'])
@jwt_required()
@role_required(['sales_officer', 'supply_chain_manager'])
def get_sales_data():
    # Get sales data
    sales_df, error = SalesService.get_sales_data()
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Convert DataFrame to list of dictionaries
    sales_data = sales_df.to_dict('records')
    
    return jsonify({
        'success': True,
        'message': 'Sales data retrieved successfully',
        'sales': sales_data
    }), 200

@sales_bp.route('/add', methods=['POST'])
@jwt_required()
@role_required('sales_officer')
def add_sale():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['date', 'store', 'item', 'sale']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Add sale
    success, message = SalesService.add_sale(
        date=data['date'],
        store=data['store'],
        item=data['item'],
        sale_amount=data['sale'],
        user_id=user_id
    )
    
    if success:
        return jsonify({'success': True, 'message': message}), 201
    else:
        return jsonify({'success': False, 'message': message}), 400

@sales_bp.route('/import', methods=['POST'])
@jwt_required()
@role_required('sales_officer')
def import_sales():
    user_id = get_jwt_identity()
    
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    # Check file extension
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'File must be a CSV'}), 400
    
    # Import sales from CSV
    success, message = SalesService.import_sales_from_csv(file, user_id)
    
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400