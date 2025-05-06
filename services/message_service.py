from models import db
from models.message import Message

class MessageService:
    @staticmethod
    def send_message(sender_id, receiver_id, subject, body):
        try:
            message = Message(
                sender_id=sender_id,
                receiver_id=receiver_id,
                subject=subject,
                body=body
            )
            db.session.add(message)
            db.session.commit()
            return True, "Message sent successfully."
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_inbox(user_id):
        try:
            messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.timestamp.desc()).all()
            return [msg.to_dict() for msg in messages], None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_sent(user_id):
        try:
            messages = Message.query.filter_by(sender_id=user_id).order_by(Message.timestamp.desc()).all()
            return [msg.to_dict() for msg in messages], None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def mark_as_read(message_id):
        try:
            message = Message.query.get(message_id)
            if message:
                message.status = 'read'
                db.session.commit()
                return True, "Marked as read"
            return False, "Message not found"
        except Exception as e:
            return False, str(e)
