from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models.user import User

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/by-role/<int:role_id>', methods=['GET'])
@jwt_required()
def get_users_by_role(role_id):
    """Fetch users based on role ID (e.g., 2 = warehouse, 3 = procurement, 4 = sales)"""
    try:
        users = User.query.filter_by(role_id=role_id).all()
        if not users:
            return jsonify({'success': False, 'message': 'No users found'}), 404

        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching users: {str(e)}'}), 500
