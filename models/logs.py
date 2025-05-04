from datetime import datetime
from . import db

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    module = db.Column(db.String(50), nullable=False)  # demand_forecast, inventory, warehouse, procurement, supplier, sales
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success, error, warning, info
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = db.relationship('User', backref='logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.username if self.user else None,
            'module': self.module,
            'action': self.action,
            'description': self.description,
            'status': self.status,
            'timestamp': self.timestamp.isoformat()
        }