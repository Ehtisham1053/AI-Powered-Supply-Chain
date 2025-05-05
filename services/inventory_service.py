import pandas as pd
from datetime import datetime
from models import db
from utils.db_utils import initialize_database
from models.inventory import Inventory, InventoryRequest
from models.sales import Forecasted7Days
from models.logs import Log

class InventoryService:

    @staticmethod
    def update_inventory(store, item, stock, user_id=None):
        """Update inventory (absolute value) for a specific store and item"""
        try:
            inventory = Inventory.query.filter_by(store=store, item=item).first()
            if not inventory:
                return False, "Inventory record not found."

            old_stock = inventory.stock_available
            inventory.stock_available = stock
            inventory.last_updated = datetime.utcnow()

            log = Log(
                user_id=user_id,
                module="inventory",
                action="update_inventory",
                description=f"Updated inventory for Store {store}, Item {item}: {old_stock} → {stock}",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            return True, "Inventory updated successfully."

        except Exception as e:
            db.session.rollback()
            log = Log(
                user_id=user_id,
                module="inventory",
                action="update_inventory",
                description=f"Error updating inventory: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            return False, f"Error updating inventory: {str(e)}"

    @staticmethod
    def get_low_stock_items(threshold=20):
        """Get inventory items with stock below the given threshold"""
        try:
            conn = initialize_database()
            cursor = conn.cursor()

            query = """
                SELECT i.id, i.store_id, s.name AS store_name, i.item_id, 
                    it.name AS item_name, i.stock, i.min_stock, i.max_stock
                FROM inventory i
                JOIN stores s ON i.store_id = s.id
                JOIN items it ON i.item_id = it.id
                WHERE i.stock <= %s
                ORDER BY i.stock ASC
            """
            cursor.execute(query, (threshold,))
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            low_stock_items = [dict(zip(columns, row)) for row in results]
            cursor.close()
            conn.close()
            return low_stock_items, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_inventory_data():
        """Fetch inventory data from the database"""
        try:
            inventory = Inventory.query.all()
            if not inventory:
                return None, "No inventory data found"

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
            inventory = Inventory.query.filter_by(store=store, item=item).first()
            if inventory:
                old_stock = inventory.stock_available
                inventory.stock_available += stock
                inventory.last_updated = datetime.utcnow()
                action_desc = f"Updated inventory for Store {store}, Item {item}: {old_stock} -> {inventory.stock_available}"
            else:
                inventory = Inventory(
                    store=store,
                    item=item,
                    stock_available=stock
                )
                db.session.add(inventory)
                action_desc = f"Added new inventory for Store {store}, Item {item}: {stock}"

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
            latest_date = db.session.query(db.func.max(Forecasted7Days.forecast_date)).scalar()
            if not latest_date:
                return False, "No forecast data found"

            forecasts = Forecasted7Days.query.filter_by(forecast_date=latest_date).all()
            if not forecasts:
                return False, "No forecast data found for the latest date"

            inventory_items = Inventory.query.all()
            if not inventory_items:
                return False, "No inventory data found"

            forecast_data = [{
                'Store': f.store,
                'Item': f.item,
                'total_7_days_prediction': round(f.total_7_days_prediction, 2)
            } for f in forecasts]

            inventory_data = [{
                'Store': i.store,
                'Item': i.item,
                'Stock_available': i.stock_available
            } for i in inventory_items]

            forecast_df = pd.DataFrame(forecast_data)
            inventory_df = pd.DataFrame(inventory_data)

            forecast_df['Store'] = forecast_df['Store'].astype(int)
            forecast_df['Item'] = forecast_df['Item'].astype(int)
            inventory_df['Store'] = inventory_df['Store'].astype(int)
            inventory_df['Item'] = inventory_df['Item'].astype(int)
            inventory_df['Stock_available'] = inventory_df['Stock_available'].astype(float)

            merged_df = pd.merge(forecast_df, inventory_df, on=['Store', 'Item'], how='outer').fillna(0)
            merged_df['Needs_restocking'] = merged_df['total_7_days_prediction'] > merged_df['Stock_available']
            merged_df['Required_quantity'] = merged_df.apply(
                lambda row: round(row['total_7_days_prediction'] - row['Stock_available'], 2)
                if row['Needs_restocking'] else 0, axis=1
            )

            restock_items = merged_df[merged_df['Needs_restocking']]
            if restock_items.empty:
                log = Log(user_id=user_id, module="inventory", action="optimize_inventory",
                          description="No items need restocking.", status="success")
                db.session.add(log)
                db.session.commit()
                return True, "Inventory optimization completed. No items need restocking."

            requests_created = 0
            for _, row in restock_items.iterrows():
                existing_request = InventoryRequest.query.filter_by(
                    store=int(row['Store']), item=int(row['Item']), status='pending').first()
                if existing_request:
                    existing_request.requested_quantity = float(row['Required_quantity'])
                    existing_request.updated_at = datetime.utcnow()
                else:
                    inventory_request = InventoryRequest(
                        store=int(row['Store']),
                        item=int(row['Item']),
                        requested_quantity=float(row['Required_quantity'])
                    )
                    db.session.add(inventory_request)
                requests_created += 1

            log = Log(user_id=user_id, module="inventory", action="optimize_inventory",
                      description=f"Created/updated {requests_created} inventory requests.",
                      status="success")
            db.session.add(log)
            db.session.commit()
            return True, f"Inventory optimization completed. Created/updated {requests_created} inventory requests."

        except Exception as e:
            db.session.rollback()
            log = Log(user_id=user_id, module="inventory", action="optimize_inventory",
                      description=f"Error optimizing inventory: {str(e)}", status="error")
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

            request_data = [request.to_dict() for request in requests]
            return request_data, None
        except Exception as e:
            return None, f"Error fetching inventory requests: {str(e)}"
