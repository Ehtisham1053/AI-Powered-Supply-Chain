from datetime import datetime
from models import db
from models.supplier import Supplier
from models.procurement import PurchaseOrder
from models.logs import Log

class SupplierService:
    @staticmethod
    def add_supplier(supplier_data, user_id=None):
        """Add a new supplier to the database"""
        try:
            # Check if supplier_id already exists
            existing_supplier = Supplier.query.filter_by(supplier_id=supplier_data['supplier_id']).first()
            
            if existing_supplier:
                return False, "Supplier ID already exists"
            
            # Create new supplier
            supplier = Supplier(
                supplier_id=supplier_data['supplier_id'],
                on_time_delivery_rate=supplier_data['on_time_delivery_rate'],
                order_accuracy_rate=supplier_data['order_accuracy_rate'],
                lead_time=supplier_data['lead_time'],
                fulfillment_rate=supplier_data['fulfillment_rate'],
                defect_rate=supplier_data['defect_rate'],
                return_rate=supplier_data['return_rate'],
                unit_price=supplier_data['unit_price'],
                responsiveness_score=supplier_data['responsiveness_score'],
                flexibility_rating=supplier_data['flexibility_rating'],
                years_in_business=supplier_data['years_in_business'],
                customer_satisfaction_rating=supplier_data['customer_satisfaction_rating']
            )
            
            db.session.add(supplier)
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="supplier",
                action="add_supplier",
                description=f"Added new Supplier {supplier_data['supplier_id']}",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, f"Supplier {supplier_data['supplier_id']} added successfully"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="supplier",
                action="add_supplier",
                description=f"Error adding Supplier {supplier_data.get('supplier_id', 'unknown')}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error adding supplier: {str(e)}"
    
    @staticmethod
    def get_suppliers(include_blacklisted=False):
        """Get all suppliers, optionally including blacklisted ones"""
        try:
            if include_blacklisted:
                suppliers = Supplier.query.all()
            else:
                suppliers = Supplier.query.filter_by(is_blacklisted=False).all()
            
            if not suppliers:
                return None, "No suppliers found"
            
            # Convert to list of dictionaries
            supplier_data = [supplier.to_dict() for supplier in suppliers]
            
            return supplier_data, None
        except Exception as e:
            return None, f"Error fetching suppliers: {str(e)}"
    
    @staticmethod
    def get_supplier_by_id(supplier_id):
        """Get a specific supplier by ID"""
        try:
            supplier = Supplier.query.filter_by(supplier_id=supplier_id).first()
            
            if not supplier:
                return None, "Supplier not found"
            
            return supplier.to_dict(), None
        except Exception as e:
            return None, f"Error fetching supplier: {str(e)}"
    
    @staticmethod
    def get_supplier_purchase_orders(supplier_id):
        """Get all purchase orders for a specific supplier"""
        try:
            purchase_orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id).all()
            
            if not purchase_orders:
                return None, "No purchase orders found for this supplier"
            
            # Convert to list of dictionaries
            po_data = [po.to_dict() for po in purchase_orders]
            
            return po_data, None
        except Exception as e:
            return None, f"Error fetching purchase orders: {str(e)}"
    
    @staticmethod
    def update_supplier(supplier_id, supplier_data, user_id=None):
        """Update an existing supplier"""
        try:
            # Get the supplier
            supplier = Supplier.query.filter_by(supplier_id=supplier_id).first()
            
            if not supplier:
                return False, "Supplier not found"
            
            # Update supplier data
            for key, value in supplier_data.items():
                if hasattr(supplier, key) and key != 'supplier_id':
                    setattr(supplier, key, value)
            
            supplier.updated_at = datetime.utcnow()
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="supplier",
                action="update_supplier",
                description=f"Updated Supplier {supplier_id}",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, f"Supplier {supplier_id} updated successfully"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="supplier",
                action="update_supplier",
                description=f"Error updating Supplier {supplier_id}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error updating supplier: {str(e)}"