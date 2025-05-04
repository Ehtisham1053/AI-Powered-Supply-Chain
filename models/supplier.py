from datetime import datetime
from . import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    on_time_delivery_rate = db.Column(db.Float, nullable=False)  # %
    order_accuracy_rate = db.Column(db.Float, nullable=False)    # %
    lead_time = db.Column(db.Float, nullable=False)              # days
    fulfillment_rate = db.Column(db.Float, nullable=False)       # %
    defect_rate = db.Column(db.Float, nullable=False)            # %
    return_rate = db.Column(db.Float, nullable=False)            # %
    unit_price = db.Column(db.Float, nullable=False)             # $
    responsiveness_score = db.Column(db.Float, nullable=False)   # 1-10
    flexibility_rating = db.Column(db.Float, nullable=False)     # 1-10
    years_in_business = db.Column(db.Float, nullable=False)
    customer_satisfaction_rating = db.Column(db.Float, nullable=False)  # 1-10
    is_blacklisted = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'on_time_delivery_rate': self.on_time_delivery_rate,
            'order_accuracy_rate': self.order_accuracy_rate,
            'lead_time': self.lead_time,
            'fulfillment_rate': self.fulfillment_rate,
            'defect_rate': self.defect_rate,
            'return_rate': self.return_rate,
            'unit_price': self.unit_price,
            'responsiveness_score': self.responsiveness_score,
            'flexibility_rating': self.flexibility_rating,
            'years_in_business': self.years_in_business,
            'customer_satisfaction_rating': self.customer_satisfaction_rating,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }