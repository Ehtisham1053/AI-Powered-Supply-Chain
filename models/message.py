from models import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages1'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='unread')  # 'unread', 'read'

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }
