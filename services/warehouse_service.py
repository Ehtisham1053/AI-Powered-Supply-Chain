import os
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
from models import db
from models.warehouse import Warehouse, Forecasted30Days, WarehouseRequest
from models.inventory import InventoryRequest, Inventory
from models.sales import Sale
from models.logs import Log
from config import Config
from utils.feature_engineering import load_and_preprocess ,add_date_features, add_sales_timeseries_metrics , create_targets
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
                    'Item': item.item,
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
    def preprocess_data_for_30day_forecast(df):
        """Preprocess sales data for 30-day forecasting"""
        try:
            # Ensure Date is datetime
            df = load_and_preprocess(df)
            df = add_sales_timeseries_metrics(df)
            df = add_date_features(df)
            df = create_targets(df)
            

            

            

            

            


            
            return df, None
        except Exception as e:
            return None, f"Error preprocessing data for 30-day forecast: {str(e)}"
    
    @staticmethod
    def forecast_30_days(user_id=None):
        """Forecast sales for the next 30 days"""
        try:
            # Get sales data
            sales = Sale.query.all()
            
            if not sales:
                return None, "No sales data found in the database"
            
            # Convert to DataFrame
            data = []
            for sale in sales:
                data.append({
                    'date': sale.date,
                    'store': sale.store,
                    'item': sale.item,
                    'sales': sale.sale
                })
            
            df = pd.DataFrame(data)
            
            # Preprocess data
            processed_df, error = WarehouseService.preprocess_data_for_30day_forecast(df)
            if error:
                return None, error
            
            # Load models from the models_30 directory
            model_dir = Config.MODELS_30_PATH
            if not os.path.exists(model_dir):
                return None, f"Model directory not found: {model_dir}"
            
            # Get unique items
            items = processed_df['item'].unique()

            
            # Initialize results dataframe
            forecast_results = pd.DataFrame(columns=['Item', 'total_predicted_sales'])
            
            # For each item, predict the next 30 days
            for item in items:
                # Filter data for this item
                item_data = processed_df[processed_df['Item'] == item]

                
                if len(item_data) < 30:  # Need at least 30 days of data
                    continue
                
                # Prepare features for prediction
                X = item_data[[
                    'Day', 'Month', 'Year', 'DayOfWeek', 'WeekOfYear', 'IsWeekend',
                    'Rolling_Mean_30d', 'Rolling_Max_30d', 'Rolling_Min_30d', 'Rolling_Std_30d'
                ]].values
                
                # Load model for this item
                store_items = processed_df[['store', 'item']].drop_duplicates()

                for _, row in store_items.iterrows():
                    store = row['store']
                    item = row['item']
                model_path = os.path.join(model_dir, f"{store}_{item}_30_day_sales.pkl")
                
                # If model doesn't exist, skip this item
                if not os.path.exists(model_path):
                    continue
                
                # Load model
                model = joblib.load(model_path)
                
                # Get the latest data point to use for prediction
                latest_data = X[-1].reshape(1, -1)
                
                # Predict the next 30 days total
                prediction = model.predict(latest_data)[0]
                
                # Add to results
                forecast_results = pd.concat([
                    forecast_results, 
                    pd.DataFrame([{
                        'Item': item,
                        'total_predicted_sales': prediction
                    }])
                ], ignore_index=True)
            
            # Save forecast to database
            forecast_date = datetime.now().date()
            
            # Check if forecast for today already exists
            existing_forecast = Forecasted30Days.query.filter_by(forecast_date=forecast_date).first()
            if existing_forecast:
                # Delete existing forecast for today
                Forecasted30Days.query.filter_by(forecast_date=forecast_date).delete()
                db.session.commit()
            
            # Save new forecast
            for _, row in forecast_results.iterrows():
                forecast = Forecasted30Days(
                    item=int(row['Item']),
                    total_predicted_sales=float(row['total_predicted_sales']),
                    forecast_date=forecast_date
                )
                db.session.add(forecast)
            
            # Log the forecast
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="generate_30_day_forecast",
                description=f"Generated 30-day forecast for {len(forecast_results)} items",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return forecast_results, None
        except Exception as e:
            # Log the error
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="generate_30_day_forecast",
                description=f"Error generating 30-day forecast: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return None, f"Error generating 30-day forecast: {str(e)}"
    
    @staticmethod
    def optimize_warehouse(user_id=None):
        """Optimize warehouse stock based on 30-day forecast"""
        try:
            # Generate 30-day forecast
            forecast_results, error = WarehouseService.forecast_30_days(user_id)
            
            if error:
                return False, error
            
            # Get current warehouse stock
            warehouse_items = Warehouse.query.all()
            
            # Convert to DataFrame
            warehouse_data = []
            for item in warehouse_items:
                warehouse_data.append({
                    'Item': item.item,
                    'Stock': item.stock
                })
            
            warehouse_df = pd.DataFrame(warehouse_data)
            
            # If warehouse is empty, initialize with zeros
            if len(warehouse_df) == 0:
                items = forecast_results['Item'].unique()
                warehouse_df = pd.DataFrame({'Item': items, 'Stock': 0})
            
            # Merge forecast and warehouse data
            merged_df = pd.merge(
                forecast_results, 
                warehouse_df, 
                on='Item', 
                how='outer'
            ).fillna(0)
            
            # Identify items that need restocking
            merged_df['Needs_restocking'] = merged_df['total_predicted_sales'] > merged_df['Stock']
            
            # Calculate required quantities
            merged_df['Required_quantity'] = merged_df.apply(
                lambda row: max(0, row['total_predicted_sales'] - row['Stock']) 
                if row['Needs_restocking'] else 0, 
                axis=1
            )
            
            # Filter items that need restocking
            restock_items = merged_df[merged_df['Needs_restocking']]
            
            if len(restock_items) == 0:
                # Log that no restocking is needed
                log = Log(
                    user_id=user_id,
                    module="warehouse",
                    action="optimize_warehouse",
                    description="Warehouse optimization completed. No items need restocking.",
                    status="success"
                )
                db.session.add(log)
                db.session.commit()
                
                return True, "Warehouse optimization completed. No items need restocking."
            
            # Create warehouse requests
            requests_created = 0
            for _, row in restock_items.iterrows():
                # Check if request already exists
                existing_request = WarehouseRequest.query.filter_by(
                    item=int(row['Item']),
                    status='pending'
                ).first()
                
                if existing_request:
                    # Update existing request
                    existing_request.requested_quantity = float(row['Required_quantity'])
                    existing_request.updated_at = datetime.utcnow()
                else:
                    # Create new request
                    warehouse_request = WarehouseRequest(
                        item=int(row['Item']),
                        requested_quantity=float(row['Required_quantity'])
                    )
                    db.session.add(warehouse_request)
                
                requests_created += 1
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="optimize_warehouse",
                description=f"Warehouse optimization completed. Created/updated {requests_created} warehouse requests.",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, f"Warehouse optimization completed. Created/updated {requests_created} warehouse requests."
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="warehouse",
                action="optimize_warehouse",
                description=f"Error optimizing warehouse: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error optimizing warehouse: {str(e)}"
    
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