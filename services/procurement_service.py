import os
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from models import db
from models.procurement import PurchaseOrder, PurchaseOrderItem
from models.warehouse import WarehouseRequest, Warehouse
from models.supplier import Supplier
from models.logs import Log
from config import Config

class ProcurementService:
    @staticmethod
    def get_warehouse_requests():
        """Get all pending warehouse requests"""
        try:
            requests = WarehouseRequest.query.filter_by(status='pending').all()
            
            if not requests:
                return None, "No pending warehouse requests found"
            
            # Convert to list of dictionaries
            request_data = [request.to_dict() for request in requests]
            
            return request_data, None
        except Exception as e:
            return None, f"Error fetching warehouse requests: {str(e)}"
    
    @staticmethod
    def evaluate_suppliers(item, user_id=None):
        """Evaluate suppliers for a specific item"""
        try:
            # Get all non-blacklisted suppliers
            suppliers = Supplier.query.filter_by(is_blacklisted=False).all()
            
            if not suppliers:
                return None, "No suppliers found"
            
            # Convert to DataFrame
            supplier_data = []
            for supplier in suppliers:
                supplier_data.append({
                    'Supplier_ID': supplier.supplier_id,
                    'On_Time_Delivery_Rate': supplier.on_time_delivery_rate,
                    'Order_Accuracy_Rate': supplier.order_accuracy_rate,
                    'Lead_Time': supplier.lead_time,
                    'Fulfillment_Rate': supplier.fulfillment_rate,
                    'Defect_Rate': supplier.defect_rate,
                    'Return_Rate': supplier.return_rate,
                    'Unit_Price': supplier.unit_price,
                    'Responsiveness_Score': supplier.responsiveness_score,
                    'Flexibility_Rating': supplier.flexibility_rating,
                    'Years_in_Business': supplier.years_in_business,
                    'Customer_Satisfaction_Rating': supplier.customer_satisfaction_rating
                })
            
            supplier_df = pd.DataFrame(supplier_data)
            # Fix column names to match model training
            supplier_df.rename(columns={
                'On_Time_Delivery_Rate': 'On_Time_Delivery_Rate (%)',
                'Order_Accuracy_Rate': 'Order_Accuracy_Rate (%)',
                'Lead_Time': 'Lead_Time (days)',
                'Fulfillment_Rate': 'Fulfillment_Rate (%)',
                'Defect_Rate': 'Defect_Rate (%)',
                'Return_Rate': 'Return_Rate (%)',
                'Unit_Price': 'Unit_Price ($)',
                'Responsiveness_Score': 'Responsiveness_Score (1-10)',
                'Flexibility_Rating': 'Flexibility_Rating (1-10)',
                'Customer_Satisfaction_Rating': 'Customer_Satisfaction_Rating (1-10)'
            }, inplace=True)
            
            # Load supplier evaluation model
            model_path = os.path.join(Config.SUPPLIER_MODEL_PATH, 'supplier_model.pkl')

            
            if not os.path.exists(model_path):
                return None, f"Supplier evaluation model not found: {model_path}"
            
            model = joblib.load(model_path)
            
            # Predict supplier scores
            X = supplier_df.drop(columns=['Supplier_ID'])
            predicted_scores = model.predict(X)
            
            # Add scores to DataFrame
            supplier_df['Predicted_Supplier_Score'] = predicted_scores
            
            # Sort by score (descending)
            ranked_suppliers = supplier_df.sort_values(by='Predicted_Supplier_Score', ascending=False)
            
            # Log the evaluation
            log = Log(
                user_id=user_id,
                module="procurement",
                action="evaluate_suppliers",
                description=f"Evaluated {len(suppliers)} suppliers for Item {item}",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return ranked_suppliers, None
        except Exception as e:
            # Log the error
            log = Log(
                user_id=user_id,
                module="procurement",
                action="evaluate_suppliers",
                description=f"Error evaluating suppliers for Item {item}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return None, f"Error evaluating suppliers: {str(e)}"
    
    @staticmethod
    def create_purchase_order(supplier_id, items, user_id=None):
        """Create a purchase order for a specific supplier"""
        try:
            # Check if supplier exists and is not blacklisted
            supplier = Supplier.query.filter_by(supplier_id=supplier_id, is_blacklisted=False).first()
            
            if not supplier:
                return None, "Supplier not found or is blacklisted"
            
            # Generate PO number (format: PO-YYYYMMDD-XXXX)
            po_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{np.random.randint(1000, 9999)}"
            
            # Calculate total amount
            total_amount = sum(item['quantity'] * supplier.unit_price for item in items)
            
            # Create purchase order
            purchase_order = PurchaseOrder(
                po_number=po_number,
                supplier_id=supplier_id,
                total_amount=total_amount
            )
            db.session.add(purchase_order)
            db.session.flush()  # Get the PO ID
            
            # Add items to purchase order
            for item_data in items:
                po_item = PurchaseOrderItem(
                    po_id=purchase_order.id,
                    item=item_data['item'],
                    quantity=item_data['quantity'],
                    unit_price=supplier.unit_price
                )
                db.session.add(po_item)
                
                # Update warehouse request status
                request = WarehouseRequest.query.filter_by(
                    item=item_data['item'],
                    status='pending'
                ).first()
                
                if request:
                    request.status = 'processing'
                    request.updated_at = datetime.utcnow()
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="procurement",
                action="create_purchase_order",
                description=f"Created Purchase Order {po_number} for Supplier {supplier_id} with {len(items)} items",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return purchase_order.to_dict(), None
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="procurement",
                action="create_purchase_order",
                description=f"Error creating purchase order for Supplier {supplier_id}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return None, f"Error creating purchase order: {str(e)}"
    
    @staticmethod
    def get_purchase_orders(supplier_id=None):
        """Get all purchase orders, optionally filtered by supplier"""
        try:
            if supplier_id:
                purchase_orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id).all()
            else:
                purchase_orders = PurchaseOrder.query.all()
            
            if not purchase_orders:
                return None, "No purchase orders found"
            
            # Convert to list of dictionaries
            po_data = [po.to_dict() for po in purchase_orders]
            
            return po_data, None
        except Exception as e:
            return None, f"Error fetching purchase orders: {str(e)}"
    
    @staticmethod
    def process_purchase_order(po_id, action, user_id=None):
        """Process a purchase order (accept or reject)"""
        try:
            # Get the purchase order
            purchase_order = PurchaseOrder.query.get(po_id)
            
            if not purchase_order:
                return False, "Purchase order not found"
            
            if purchase_order.status not in ['pending', 'rejected']:
                return False, f"Purchase order is already {purchase_order.status}"
            
            if action == 'accept':
                # Update purchase order status
                purchase_order.status = 'accepted'
                purchase_order.updated_at = datetime.utcnow()
                
                # Log the action
                log = Log(
                    user_id=user_id,
                    module="procurement",
                    action="process_purchase_order",
                    description=f"Accepted Purchase Order {purchase_order.po_number}",
                    status="success"
                )
                db.session.add(log)
                db.session.commit()
                
                return True, f"Purchase order {purchase_order.po_number} accepted"
            elif action == 'reject':
                # Update purchase order status
                purchase_order.status = 'rejected'
                purchase_order.updated_at = datetime.utcnow()
                
                # Update warehouse requests back to pending
                for po_item in purchase_order.items:
                    request = WarehouseRequest.query.filter_by(
                        item=po_item.item,
                        status='processing'
                    ).first()
                    
                    if request:
                        request.status = 'pending'
                        request.updated_at = datetime.utcnow()
                
                # Log the action
                log = Log(
                    user_id=user_id,
                    module="procurement",
                    action="process_purchase_order",
                    description=f"Rejected Purchase Order {purchase_order.po_number}",
                    status="warning"
                )
                db.session.add(log)
                db.session.commit()
                
                return True, f"Purchase order {purchase_order.po_number} rejected"
            elif action == 'complete':
                # Update purchase order status
                purchase_order.status = 'completed'
                purchase_order.updated_at = datetime.utcnow()
                
                # Update warehouse stock
                for po_item in purchase_order.items:
                    # Get warehouse item
                    warehouse_item = Warehouse.query.filter_by(item=po_item.item).first()
                    
                    if warehouse_item:
                        # Update existing record
                        warehouse_item.stock += po_item.quantity
                        warehouse_item.last_updated = datetime.utcnow()
                    else:
                        # Create new record
                        warehouse_item = Warehouse(
                            item=po_item.item,
                            stock=po_item.quantity
                        )
                        db.session.add(warehouse_item)
                    
                    # Update warehouse request status
                    request = WarehouseRequest.query.filter_by(
                        item=po_item.item,
                        status='processing'
                    ).first()
                    
                    if request:
                        request.status = 'completed'
                        request.updated_at = datetime.utcnow()
                
                # Log the action
                log = Log(
                    user_id=user_id,
                    module="procurement",
                    action="process_purchase_order",
                    description=f"Completed Purchase Order {purchase_order.po_number}",
                    status="success"
                )
                db.session.add(log)
                db.session.commit()
                
                return True, f"Purchase order {purchase_order.po_number} completed and warehouse stock updated"
            else:
                return False, f"Invalid action: {action}"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="procurement",
                action="process_purchase_order",
                description=f"Error processing purchase order #{po_id}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error processing purchase order: {str(e)}"
    
    @staticmethod
    def blacklist_supplier(supplier_id, blacklist, user_id=None):
        """Blacklist or un-blacklist a supplier"""
        try:
            # Get the supplier
            supplier = Supplier.query.filter_by(supplier_id=supplier_id).first()
            
            if not supplier:
                return False, "Supplier not found"
            
            # Update blacklist status
            supplier.is_blacklisted = blacklist
            supplier.updated_at = datetime.utcnow()
            
            # Log the action
            action = "blacklist" if blacklist else "un-blacklist"
            log = Log(
                user_id=user_id,
                module="procurement",
                action=f"{action}_supplier",
                description=f"{action.capitalize()}ed Supplier {supplier_id}",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, f"Supplier {supplier_id} {action}ed successfully"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            action = "blacklist" if blacklist else "un-blacklist"
            log = Log(
                user_id=user_id,
                module="procurement",
                action=f"{action}_supplier",
                description=f"Error {action}ing Supplier {supplier_id}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error {action}ing supplier: {str(e)}"