from datetime import datetime
from . import db

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(20), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, accepted, rejected, completed
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'po_number': self.po_number,
            'supplier_id': self.supplier_id,
            'status': self.status,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    item = db.Column(db.Integer, nullable=False)  # 1-50
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'po_id': self.po_id,
            'item': self.item,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.quantity * self.unit_price
        }