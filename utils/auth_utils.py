from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def role_required(roles):
    """
    Decorator to check if the user has the required role(s)
    
    Args:
        roles: A string or list of strings representing the required role(s)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Get JWT claims
            claims = get_jwt()
            user_role = claims.get('role')
            
            # Convert roles to list if it's a string
            required_roles = roles if isinstance(roles, list) else [roles]
            
            # Check if user has one of the required roles
            if user_role not in required_roles:
                return jsonify({
                    'success': False,
                    'message': 'Access denied: insufficient permissions'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator