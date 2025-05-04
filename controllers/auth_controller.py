from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auth_service import AuthService
from models.user import User

# Define the blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['username', 'email', 'password', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

    if data['role'] == 'supplier' and 'supplier_id' not in data:
        return jsonify({'success': False, 'message': 'Supplier ID is required for supplier role'}), 400

    response = AuthService.register_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data['role'],
        supplier_id=data.get('supplier_id')
    )

    return jsonify(response), 201 if response.get("success") else 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    result = AuthService.login_user(
        username=data['username'],
        password=data['password']
    )

    return jsonify(result), 200 if result['success'] else 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({'success': True, 'user': user.to_dict()}), 200

@auth_bp.route('/check-role', methods=['GET'])
@jwt_required()
def check_role():
    claims = get_jwt()
    return jsonify({
        'success': True,
        'role': claims.get('role'),
        'supplier_id': claims.get('supplier_id')
    }), 200
