import pandas as pd
from datetime import datetime
from models import db
from models.inventory import Inventory, InventoryRequest
from models.sales import Forecasted7Days
from models.logs import Log

class InventoryService:
    @staticmethod
    def get_inventory_data():
        """Fetch inventory data from the database"""
        try:
            inventory = Inventory.query.all()
            
            if not inventory:
                return None, "No inventory data found"
            
            # Convert to DataFrame
            data = []
            for item in inventory:
                data.append({
                    'Store': item.store,
                    'Item': item.item,
                    'Stock_available': item.stock_available,
                    'Last_updated': item.last_updated
                })
            
            df = pd.DataFrame(data)
            return df, None
        except Exception as e:
            return None, f"Error fetching inventory data: {str(e)}"
    
    @staticmethod
    def add_inventory(store, item, stock, user_id=None):
        """Add or update inventory for a specific store and item"""
        try:
            # Check if inventory record exists
            inventory = Inventory.query.filter_by(store=store, item=item).first()
            
            if inventory:
                # Update existing record
                old_stock = inventory.stock_available
                inventory.stock_available += stock
                inventory.last_updated = datetime.utcnow()
                action_desc = f"Updated inventory for Store {store}, Item {item}: {old_stock} -> {inventory.stock_available}"
            else:
                # Create new record
                inventory = Inventory(
                    store=store,
                    item=item,
                    stock_available=stock
                )
                db.session.add(inventory)
                action_desc = f"Added new inventory for Store {store}, Item {item}: {stock}"
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="inventory",
                action="add_inventory",
                description=action_desc,
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, "Inventory updated successfully"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="inventory",
                action="add_inventory",
                description=f"Error updating inventory for Store {store}, Item {item}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error updating inventory: {str(e)}"
    
    @staticmethod
    def optimize_inventory(user_id=None):
        """Optimize inventory based on 7-day forecast"""
        try:
            # Get latest forecast
            latest_date = db.session.query(db.func.max(Forecasted7Days.forecast_date)).scalar()
            
            if not latest_date:
                return False, "No forecast data found"
            
            forecasts = Forecasted7Days.query.filter_by(forecast_date=latest_date).all()
            
            if not forecasts:
                return False, "No forecast data found for the latest date"
            
            # Get current inventory
            inventory_items = Inventory.query.all()
            
            if not inventory_items:
                return False, "No inventory data found"
            
            # Convert to DataFrames
            forecast_data = []
            for forecast in forecasts:
                forecast_data.append({
                    'Store': forecast.store,
                    'Item': forecast.item,
                    'total_7_days_prediction': forecast.total_7_days_prediction
                })
            
            forecast_df = pd.DataFrame(forecast_data)
            
            inventory_data = []
            for item in inventory_items:
                inventory_data.append({
                    'Store': item.store,
                    'Item': item.item,
                    'Stock_available': item.stock_available
                })
            
            inventory_df = pd.DataFrame(inventory_data)
            
            # Merge forecast and inventory data
            merged_df = pd.merge(
                forecast_df, 
                inventory_df, 
                on=['Store', 'Item'], 
                how='outer'
            ).fillna(0)
            
            # Identify items that need restocking
            merged_df['Needs_restocking'] = merged_df['total_7_days_prediction'] > merged_df['Stock_available']
            
            # Calculate required quantities
            merged_df['Required_quantity'] = merged_df.apply(
                lambda row: max(0, row['total_7_days_prediction'] - row['Stock_available']) 
                if row['Needs_restocking'] else 0, 
                axis=1
            )
            
            # Filter items that need restocking
            restock_items = merged_df[merged_df['Needs_restocking']]
            
            if len(restock_items) == 0:
                # Log that no restocking is needed
                log = Log(
                    user_id=user_id,
                    module="inventory",
                    action="optimize_inventory",
                    description="Inventory optimization completed. No items need restocking.",
                    status="success"
                )
                db.session.add(log)
                db.session.commit()
                
                return True, "Inventory optimization completed. No items need restocking."
            
            # Create inventory requests
            requests_created = 0
            for _, row in restock_items.iterrows():
                # Check if request already exists
                existing_request = InventoryRequest.query.filter_by(
                    store=int(row['Store']),
                    item=int(row['Item']),
                    status='pending'
                ).first()
                
                if existing_request:
                    # Update existing request
                    existing_request.requested_quantity = float(row['Required_quantity'])
                    existing_request.updated_at = datetime.utcnow()
                else:
                    # Create new request
                    inventory_request = InventoryRequest(
                        store=int(row['Store']),
                        item=int(row['Item']),
                        requested_quantity=float(row['Required_quantity'])
                    )
                    db.session.add(inventory_request)
                
                requests_created += 1
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="inventory",
                action="optimize_inventory",
                description=f"Inventory optimization completed. Created/updated {requests_created} inventory requests.",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, f"Inventory optimization completed. Created/updated {requests_created} inventory requests."
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="inventory",
                action="optimize_inventory",
                description=f"Error optimizing inventory: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error optimizing inventory: {str(e)}"
    
    @staticmethod
    def get_inventory_requests():
        """Get all pending inventory requests"""
        try:
            requests = InventoryRequest.query.filter_by(status='pending').all()
            
            if not requests:
                return None, "No pending inventory requests found"
            
            # Convert to list of dictionaries
            request_data = [request.to_dict() for request in requests]
            
            return request_data, None
        except Exception as e:
            return None, f"Error fetching inventory requests: {str(e)}"