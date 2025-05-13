from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.log_service import LogService
from utils.auth_utils import role_required
import csv
import io

# Correct Blueprint setup
log_bp = Blueprint('log', __name__, url_prefix='/api/logs')

@log_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('warehouse_team')
def get_logs():
    module = request.args.get('module', 'warehouse')
    user_id = get_jwt_identity()

    logs, error = LogService.get_logs(module=module, user_id=user_id)
    print("✅ LOGS FETCHED:", logs)  # DEBUG LINE

    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'message': 'Logs retrieved successfully',
        'logs': logs
    }), 200


@log_bp.route('/module/<module>', methods=['GET'])
@jwt_required()
@role_required('supply_chain_manager')
def get_logs_by_module(module):
    # Get query parameters
    limit = request.args.get('limit', 100, type=int)
    
    # Get logs for specific module
    logs, error = LogService.get_logs(module=module, limit=limit)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': f'Logs for module {module} retrieved successfully',
        'logs': logs
    }), 200

@log_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required('supply_chain_manager')
def get_logs_by_user(user_id):
    # Get query parameters
    limit = request.args.get('limit', 100, type=int)
    
    # Get logs for specific user
    logs, error = LogService.get_logs(user_id=user_id, limit=limit)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    return jsonify({
        'success': True,
        'message': f'Logs for user {user_id} retrieved successfully',
        'logs': logs
    }), 200

@log_bp.route('/download', methods=['GET'])
@jwt_required()
def download_logs():
    claims = get_jwt()
    role = claims.get('role')
    user_id = get_jwt_identity()
    
    # For supply chain manager, allow downloading all logs
    if role == 'supply_chain_manager':
        module = request.args.get('module')
        target_user_id = request.args.get('user_id')
        logs, error = LogService.get_logs(module, target_user_id, limit=None)
    else:
        # For other roles, only allow downloading their own logs
        logs, error = LogService.get_logs(user_id=user_id, limit=None)
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
    
    # Convert logs to CSV format
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'User', 'Module', 'Action', 'Description', 'Status', 'Timestamp'])
    
    # Write data
    for log in logs:
        writer.writerow([
            log['id'],
            log['user'],
            log['module'],
            log['action'],
            log['description'],
            log['status'],
            log['timestamp']
        ])
    
    # Create response
    from flask import Response
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=logs.csv'
        }
    )




@log_bp.route('/all', methods=['GET'])
@jwt_required()
@role_required('supply_chain_manager')
def get_all_system_logs():
    """Fetch all system logs for Supply Chain Manager"""
    module = request.args.get('module')
    user_id = request.args.get('user_id')
    limit = request.args.get('limit', 100, type=int)

    logs, error = LogService.get_logs(module=module, user_id=user_id, limit=limit)

    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'message': 'System logs retrieved successfully',
        'logs': logs
    }), 200



@log_bp.route('/procurement-officer', methods=['GET'])
@jwt_required()
@role_required('procurement_officer')
def get_procurement_officer_logs():
    user_id = get_jwt_identity()

    logs, error = LogService.get_logs(module="procurement", user_id=user_id)

    if error:
        return jsonify({"success": False, "message": error}), 400

    return jsonify({
        "success": True,
        "message": "Procurement logs retrieved successfully",
        "logs": logs
    }), 200

@log_bp.route('/download/procurement-officer', methods=['GET'])
@jwt_required()
@role_required('procurement_officer')
def download_procurement_logs():
    user_id = get_jwt_identity()

    logs, error = LogService.get_logs(module="procurement", user_id=user_id, limit=None)

    if error:
        return jsonify({'success': False, 'message': error}), 400

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['ID', 'User', 'Module', 'Action', 'Description', 'Status', 'Timestamp'])

    for log in logs:
        writer.writerow([
            log['id'],
            log['user'],
            log['module'],
            log['action'],
            log['description'],
            log['status'],
            log['timestamp']
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=procurement_logs.csv'
        }
    )



@log_bp.route('/sales-officer', methods=['GET'])
@jwt_required()
@role_required('sales_officer')
def get_sales_officer_logs():
    user_id = get_jwt_identity()
    logs, error = LogService.get_sales_logs(user_id=user_id)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    return jsonify({
        'success': True,
        'message': 'Sales logs retrieved successfully',
        'logs': logs
    }), 200
