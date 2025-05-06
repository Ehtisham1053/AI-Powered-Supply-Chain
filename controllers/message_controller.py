from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.message_service import MessageService

message_bp = Blueprint('message', __name__, url_prefix='/api/messages')

@message_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    sender_id = get_jwt_identity()
    receiver_id = data.get('receiver_id')
    subject = data.get('subject')
    body = data.get('body')

    if not all([receiver_id, subject, body]):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    success, message = MessageService.send_message(sender_id, receiver_id, subject, body)
    return jsonify({'success': success, 'message': message}), 200 if success else 400

@message_bp.route('/inbox', methods=['GET'])
@jwt_required()
def inbox():
    user_id = get_jwt_identity()
    messages, error = MessageService.get_inbox(user_id)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'messages': messages})

@message_bp.route('/sent', methods=['GET'])
@jwt_required()
def sent():
    user_id = get_jwt_identity()
    messages, error = MessageService.get_sent(user_id)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'messages': messages})

@message_bp.route('/mark-read/<int:message_id>', methods=['PUT'])
@jwt_required()
def mark_as_read(message_id):
    success, msg = MessageService.mark_as_read(message_id)
    return jsonify({'success': success, 'message': msg}), 200 if success else 400




