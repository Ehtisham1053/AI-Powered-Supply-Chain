from datetime import datetime
from . import db
from models import db  # ✅ Correct import to avoid circular reference


class POSupplier(db.Model):
    __tablename__ = 'po_supplier'

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.Integer, nullable=False)
    supplier_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'confirmed' or 'rejected'
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'item': self.item,
            'supplier_id': self.supplier_id,
            'quantity': self.quantity,
            'status': self.status,
            'processed_at': self.processed_at.isoformat()
        }
