from datetime import datetime
from . import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    store = db.Column(db.Integer, nullable=False)  # 1-10
    item = db.Column(db.Integer, nullable=False)   # 1-50
    stock_available = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('store', 'item', name='uix_store_item'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'store': self.store,
            'item': self.item,
            'stock_available': self.stock_available,
            'last_updated': self.last_updated.isoformat()
        }

class InventoryRequest(db.Model):
    __tablename__ = 'inventory_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    store = db.Column(db.Integer, nullable=False)  # 1-10
    item = db.Column(db.Integer, nullable=False)   # 1-50
    requested_quantity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'store': self.store,
            'item': self.item,
            'requested_quantity': self.requested_quantity,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }