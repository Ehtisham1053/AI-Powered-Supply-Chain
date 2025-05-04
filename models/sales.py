from datetime import datetime
from . import db

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    store = db.Column(db.Integer, nullable=False)  # 1-10
    item = db.Column(db.Integer, nullable=False)   # 1-50
    sale = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'store': self.store,
            'item': self.item,
            'sale': self.sale,
            'created_at': self.created_at.isoformat()
        }

class Forecasted7Days(db.Model):
    __tablename__ = 'forecasted_7_days'
    
    id = db.Column(db.Integer, primary_key=True)
    store = db.Column(db.Integer, nullable=False)  # 1-10
    item = db.Column(db.Integer, nullable=False)   # 1-50
    total_7_days_prediction = db.Column(db.Float, nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'store': self.store,
            'item': self.item,
            'total_7_days_prediction': self.total_7_days_prediction,
            'forecast_date': self.forecast_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }