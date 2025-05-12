import os
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
from tqdm import tqdm

from models import db
from models.warehouse import Warehouse, Forecasted30Days, WarehouseRequest
from models.inventory import InventoryRequest, Inventory
from models.sales import Sale
from models.logs import Log
from config import Config
from utils.feature_engineering import load_and_preprocess ,add_date_features, add_sales_timeseries_metrics , create_targets , forecast_future_30
class WarehouseService:
    @staticmethod
    def get_warehouse_data():
        """Fetch warehouse data from the database"""
        try:
            warehouse_items = Warehouse.query.all()
            
            if not warehouse_items:
                return None, "No warehouse data found"
            
            # Convert to DataFrame
            data = []
            for item in warehouse_items:
                data.append({
                    'item': item.item,
                    'Stock': item.stock,
                    'Last_updated': item.last_updated
                })
            
            df = pd.DataFrame(data)
            return df, None
        except Exception as e:
            return None, f"Error fetching warehouse data: {str(e)}"
    
    @staticmethod
    def add_warehouse_stock(item, stock, user_id=None):
        """Add or update stock for a specific item in the warehouse"""
        try:
            # Check if warehouse record exists
            warehouse_item = Warehouse.query.filter_by(item=item).first()
            
            if warehouse_item:
                # Update existing record
                old_stock = warehouse_item.stock
                warehouse_item.stock += stock
                warehouse_item.last_updated = datetime.utcnow()
                action_desc = f"Updated warehouse stock for Item {item}: {old_stock} -> {warehouse_item.stock}"
            else:
                # Create new record
                warehouse_item = Warehouse(
                    item=item,
                    stock=stock
                )
                db.session.add(warehouse_item)
                action_desc = f"Added new warehouse stock for Item {item}: {stock}"
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="add_warehouse_stock",
                description=action_desc,
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, "Warehouse stock updated successfully"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="add_warehouse_stock",
                description=f"Error updating warehouse stock for Item {item}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error updating warehouse stock: {str(e)}"
    
    @staticmethod
    def process_inventory_request(request_id, approve, user_id=None):
        """Process an inventory request (approve or reject)"""
        try:
            # Get the request
            inventory_request = InventoryRequest.query.get(request_id)
            
            if not inventory_request:
                return False, "Inventory request not found"
            
            if inventory_request.status != 'pending':
                return False, "Inventory request is not pending"
            
            if approve:
                # Check if warehouse has enough stock
                warehouse_item = Warehouse.query.filter_by(item=inventory_request.item).first()
                
                if not warehouse_item or warehouse_item.stock < inventory_request.requested_quantity:
                    # Update request status to rejected
                    inventory_request.status = 'rejected'
                    inventory_request.updated_at = datetime.utcnow()
                    
                    # Log the action
                    log = Log(
                        user_id=user_id,
                        module="warehouse",
                        action="process_inventory_request",
                        description=f"Rejected inventory request #{request_id} due to insufficient warehouse stock",
                        status="warning"
                    )
                    db.session.add(log)
                    db.session.commit()
                    
                    return False, "Insufficient warehouse stock to fulfill request"
                
                # Update warehouse stock
                warehouse_item.stock -= inventory_request.requested_quantity
                warehouse_item.last_updated = datetime.utcnow()
                
                # Update inventory
                inventory = Inventory.query.filter_by(
                    store=inventory_request.store,
                    item=inventory_request.item
                ).first()
                
                if inventory:
                    # Update existing inventory
                    inventory.stock_available += inventory_request.requested_quantity
                    inventory.last_updated = datetime.utcnow()
                else:
                    # Create new inventory record
                    inventory = Inventory(
                        store=inventory_request.store,
                        item=inventory_request.item,
                        stock_available=inventory_request.requested_quantity
                    )
                    db.session.add(inventory)
                
                # Update request status to approved
                inventory_request.status = 'approved'
                inventory_request.updated_at = datetime.utcnow()
                
                # Log the action
                log = Log(
                    user_id=user_id,
                    module="warehouse",
                    action="process_inventory_request",
                    description=f"Approved inventory request #{request_id}. Transferred {inventory_request.requested_quantity} units of Item {inventory_request.item} to Store {inventory_request.store}",
                    status="success"
                )
                db.session.add(log)
                db.session.commit()
                
                return True, f"Inventory request approved and stock transferred"
            else:
                # Update request status to rejected
                inventory_request.status = 'rejected'
                inventory_request.updated_at = datetime.utcnow()
                
                # Log the action
                log = Log(
                    user_id=user_id,
                    module="warehouse",
                    action="process_inventory_request",
                    description=f"Rejected inventory request #{request_id}",
                    status="info"
                )
                db.session.add(log)
                db.session.commit()
                
                return True, "Inventory request rejected"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="process_inventory_request",
                description=f"Error processing inventory request #{request_id}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error processing inventory request: {str(e)}"
    

    
    @staticmethod
    def preprocess_data_for_30day_forecast():
        """Fetch sales data and preprocess it for 30-day forecasting"""
        try:
            # Fetch sales data from DB
            sales = Sale.query.all()
            if not sales:
                return None, "No sales data found in the database"

            # Convert to DataFrame
            data = [
                {
                    'date': sale.date,
                    'store': sale.store,
                    'item': sale.item,
                    'sales': sale.sale
                }
                for sale in sales
            ]
            df = pd.DataFrame(data)

            # Apply preprocessing pipeline
            df = load_and_preprocess(df)
            df = add_sales_timeseries_metrics(df)
            df = add_date_features(df)
            df = create_targets(df)

            return df, None
        except Exception as e:
            return None, f"Error during preprocessing: {str(e)}"
        






    @staticmethod
    def forecast_30_days(user_id=None):
        """Run 30-day forecast, store it, and return as list of dictionaries"""
        try:
            processed_df, error = WarehouseService.preprocess_data_for_30day_forecast()
            if error:
                return None, error

            forecast_results = forecast_future_30(
                df=processed_df,
                target_col="target_30_day_sales",
                forecast_days=30,
                model_dir=Config.MODELS_30_PATH
            )

            if forecast_results.empty:
                return None, "No forecast generated. Ensure sales data is sufficient and models exist."

            forecast_date = datetime.now().date()

            # Remove existing forecast for the same date to avoid duplicates
            Forecasted30Days.query.filter_by(forecast_date=forecast_date).delete()
            db.session.commit()

            # Save forecast to DB
            for _, row in forecast_results.iterrows():
                forecast = Forecasted30Days(
                    item=int(row['item']),
                    total_predicted_sales=float(row['total_predicted_sales']),
                    forecast_date=forecast_date
                )
                db.session.add(forecast)

            # Log the forecast generation
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="generate_30_day_forecast",
                description=f"Forecast saved for {len(forecast_results)} items.",
                status="success"
            )
            db.session.add(log)
            db.session.commit()

            # ✅ Attach forecast_date to each record for frontend
            forecast_results['forecast_date'] = forecast_date.strftime("%Y-%m-%d")
            forecast_display = forecast_results.to_dict(orient="records")

            return forecast_display, None

        except Exception as e:
            db.session.rollback()
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="generate_30_day_forecast",
                description=f"Error: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            return None, f"Error generating 30-day forecast: {str(e)}"




    @staticmethod
    def optimize_warehouse(user_id=None):
        """Optimize warehouse stock based on 30-day forecast and create warehouse restock requests"""
        try:
            # Generate forecast
            forecast_results, error = WarehouseService.forecast_30_days(user_id)
            if error:
                return False, error

            # Get current warehouse stock
            warehouse_items = Warehouse.query.all()
            warehouse_data = [{'item': w.item, 'Stock': w.stock} for w in warehouse_items]
            warehouse_df = pd.DataFrame(warehouse_data)

            # If no stock in warehouse, initialize with zeros for each item in forecast
            if warehouse_df.empty:
                item_ids = [row['item'] for row in forecast_results]
                warehouse_df = pd.DataFrame({'item': item_ids, 'Stock': 0})

            # Merge forecast with current stock
            forecast_df = pd.DataFrame(forecast_results)
            merged_df = pd.merge(forecast_df, warehouse_df, on='item', how='outer').fillna(0)

            # Identify restocking needs
            merged_df['Needs_restocking'] = merged_df['total_predicted_sales'] > merged_df['Stock']
            merged_df['Required_quantity'] = merged_df.apply(
                lambda row: max(0, row['total_predicted_sales'] - row['Stock']) if row['Needs_restocking'] else 0,
                axis=1
            )

            restock_items = merged_df[merged_df['Needs_restocking']]
            print(merged_df[['item', 'total_predicted_sales', 'Stock', 'Needs_restocking']])
            print("\n=== Optimization Debug Output ===")
            print(merged_df[['item', 'total_predicted_sales', 'Stock', 'Needs_restocking', 'Required_quantity']])
            print("Restock Items:\n", restock_items)
            print(f"Total restock items: {len(restock_items)}")
            if restock_items.empty:
                log = Log(
                    user_id=user_id,
                    module="warehouse",
                    action="optimize_warehouse",
                    description="No items need restocking.",
                    status="success"
                )
                db.session.add(log)
                db.session.commit()
                return True, "Warehouse optimization completed. No restocking needed."

            # Add to warehouse_requests table
            requests_created = 0
            for _, row in restock_items.iterrows():
                item_id = int(row['item'])
                qty = float(row['Required_quantity'])

                existing_request = WarehouseRequest.query.filter_by(item=item_id, status='pending').first()
                if existing_request:
                    existing_request.requested_quantity = qty
                    existing_request.updated_at = datetime.utcnow()
                else:
                    request = WarehouseRequest(
                        item=item_id,
                        requested_quantity=qty
                    )
                    db.session.add(request)
                requests_created += 1

            # Log optimization
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="optimize_warehouse",
                description=f"Created/updated {requests_created} warehouse restock requests.",
                status="success"
            )
            db.session.add(log)
            db.session.commit()

            return True, f"Warehouse optimization completed. {requests_created} restock requests recorded."
        except Exception as e:
            db.session.rollback()
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="optimize_warehouse",
                description=f"Error optimizing warehouse: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            return False, f"Error: {str(e)}"










            

    
 
    
    @staticmethod
    def get_warehouse_requests():
        """Get all pending warehouse requests"""
        try:
            requests = InventoryRequest.query.filter_by(status='pending').all()

            
            if not requests:
                return None, "No pending warehouse requests found"
            
            # Convert to list of dictionaries
            request_data = [request.to_dict() for request in requests]
            
            return request_data, None
        except Exception as e:
            return None, f"Error fetching warehouse requests: {str(e)}"
        



    @staticmethod
    def get_optimization_status():
        """Compare forecasted sales and warehouse stock; return items needing restocking"""
        try:
            # Get forecasted sales
            forecasts = Forecasted30Days.query.all()
            warehouse = Warehouse.query.all()

            if not forecasts or not warehouse:
                return None, "Forecast or warehouse data missing"

            # Convert to DataFrames
            forecast_df = pd.DataFrame([{
                'item': f.item,
                'total_predicted_sales': f.total_predicted_sales
            } for f in forecasts])

            warehouse_df = pd.DataFrame([{
                'item': w.item,
                'stock': w.stock
            } for w in warehouse])

            # Merge and fill missing stock with 0
            merged = pd.merge(forecast_df, warehouse_df, on='item', how='left').fillna(0)

            # Calculate restocking need
            merged['required_quantity'] = merged['total_predicted_sales'] - merged['stock']
            merged['required_quantity'] = merged['required_quantity'].apply(lambda x: max(0, x))

            # Assign status
            merged['status'] = merged['required_quantity'].apply(
                lambda x: 'danger' if x > 0 else 'success'
            )

            return merged.to_dict(orient="records"), None

        except Exception as e:
            return None, f"Error in warehouse optimization status: {str(e)}"
