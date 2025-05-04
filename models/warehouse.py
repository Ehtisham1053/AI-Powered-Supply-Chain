from datetime import datetime
from . import db

class Warehouse(db.Model):
    __tablename__ = 'warehouse'
    
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.Integer, nullable=False, unique=True)  # 1-50
    stock = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item': self.item,
            'stock': self.stock,
            'last_updated': self.last_updated.isoformat()
        }

class Forecasted30Days(db.Model):
    __tablename__ = 'forecasted_30_days'
    
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.Integer, nullable=False)  # 1-50
    total_predicted_sales = db.Column(db.Float, nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('item', 'forecast_date', name='uix_item_forecast_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'item': self.item,
            'total_predicted_sales': self.total_predicted_sales,
            'forecast_date': self.forecast_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

class WarehouseRequest(db.Model):
    __tablename__ = 'warehouse_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.Integer, nullable=False)  # 1-50
    requested_quantity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item': self.item,
            'requested_quantity': self.requested_quantity,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }