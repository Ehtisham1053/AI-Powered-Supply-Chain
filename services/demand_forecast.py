import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
from models import db
from models.sales import Sale, Forecasted7Days
from models.logs import Log
from config import Config
from utils.feature_engineering import add_sales_timeseries_metrics, add_date_features ,create_targets, load_and_preprocess
class DemandForecastService:
    @staticmethod
    def get_sales_data():
        """Fetch sales data from the database and convert to DataFrame"""
        try:
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
            return df, None
        except Exception as e:
            return None, f"Error fetching sales data: {str(e)}"
    
    @staticmethod
    def preprocess_data(df):
        """Preprocess sales data for forecasting"""
        try:
            df = load_and_preprocess(df)
            df = add_sales_timeseries_metrics(df)
            df = add_date_features(df)
            df = create_targets(df)


            
            # Fill NaN values
            df = df.fillna(0)
            
            return df, None
        except Exception as e:
            return None, f"Error preprocessing data: {str(e)}"
    
    @staticmethod
    def forecast_7_days(df, user_id=None):
        """Forecast sales for the next 7 days"""
        try:
            # Preprocess data
            processed_df, error = DemandForecastService.preprocess_data(df)
            if error:
                return None, error
            
            # Load models from the models_7 directory
            model_dir = Config.MODELS_7_PATH
            if not os.path.exists(model_dir):
                return None, f"Model directory not found: {model_dir}"
            
            # Get unique store-item combinations
            store_items = processed_df[['store', 'item']].drop_duplicates()
            
            # Initialize results dataframe
            forecast_results = pd.DataFrame(columns=['Store', 'Item', 'total_7_days_prediction'])
            
            # For each store-item combination, predict the next 7 days
            for _, row in store_items.iterrows():
                store = row['store']
                item = row['item']
                
                # Filter data for this store and item
                item_data = processed_df[(processed_df['store'] == store) & (processed_df['item'] == item)]
                
                if len(item_data) < 7:  # Need at least 7 days of data
                    continue
                
                # Prepare features for prediction
                X = item_data[[  # ✅ correct
                    'sales_1_day_ago', 'sales_7_days_ago', 'rolling_14_day_sales',
                    'rolling_28_day_sales', 'mean_sales', 'day', 'month', 'year',
                    'day_of_week', 'weekend', 'quarter'
                ]].values

                
                # Load model for this store-item combination
                model_path = os.path.join(model_dir, f"{store}_{item}_target_7_day_sales.pkl")

                
                # If model doesn't exist, skip this combination
                if not os.path.exists(model_path):
                    print(f"Model not found for Store: {store}, Item: {item}")
                    continue

                
                # Load model
                model = joblib.load(model_path)
                
                # Get the latest data point to use for prediction
                latest_data = X[-1].reshape(1, -1)
                
                # Predict the next 7 days total
                prediction = model.predict(latest_data)[0]
                
                # Add to results
                forecast_results = pd.concat([
                    forecast_results, 
                    pd.DataFrame([{
                        'Store': store,
                        'Item': item,
                        'total_7_days_prediction': prediction
                    }])
                ], ignore_index=True)
            
            # Save forecast to database
            forecast_date = datetime.now().date()
            
            # Check if forecast for today already exists
            existing_forecast = Forecasted7Days.query.filter_by(forecast_date=forecast_date).first()
            if existing_forecast:
                # Delete existing forecast for today
                Forecasted7Days.query.filter_by(forecast_date=forecast_date).delete()
                db.session.commit()
            
            # Save new forecast
            for _, row in forecast_results.iterrows():
                forecast = Forecasted7Days(
                    store=int(row['Store']),
                    item=int(row['Item']),
                    total_7_days_prediction=float(row['total_7_days_prediction']),
                    forecast_date=forecast_date
                )
                db.session.add(forecast)
            
            # Log the forecast
            log = Log(
                user_id=user_id,
                module="demand_forecast",
                action="generate_7_day_forecast",
                description=f"Generated 7-day forecast for {len(forecast_results)} store-item combinations",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return forecast_results, None
        except Exception as e:
            # Log the error
            log = Log(
                user_id=user_id,
                module="demand_forecast",
                action="generate_7_day_forecast",
                description=f"Error generating 7-day forecast: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return None, f"Error generating forecast: {str(e)}"
    
    @staticmethod
    def get_latest_forecast():
        """Get the latest 7-day forecast from the database"""
        try:
            # Get the latest forecast date
            latest_date = db.session.query(db.func.max(Forecasted7Days.forecast_date)).scalar()
            
            if not latest_date:
                return None, "No forecast data found"
            
            # Get forecast for the latest date
            forecasts = Forecasted7Days.query.filter_by(forecast_date=latest_date).all()
            
            if not forecasts:
                return None, "No forecast data found for the latest date"
            
            # Convert to DataFrame
            data = []
            for forecast in forecasts:
                data.append({
                    'Store': forecast.store,
                    'Item': forecast.item,
                    'total_7_days_prediction': forecast.total_7_days_prediction,
                    'forecast_date': forecast.forecast_date
                })
            
            df = pd.DataFrame(data)
            return df, None
        except Exception as e:
            return None, f"Error fetching latest forecast: {str(e)}"
    
    @staticmethod
    def delete_forecast_by_date(date, user_id=None):
        """Delete forecast for a specific date"""
        try:
            # Convert string date to date object if needed
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Delete forecast for the specified date
            deleted = Forecasted7Days.query.filter_by(forecast_date=date).delete()
            
            if deleted == 0:
                return False, "No forecast found for the specified date"
            
            # Log the deletion
            log = Log(
                user_id=user_id,
                module="demand_forecast",
                action="delete_forecast",
                description=f"Deleted forecast for date {date}",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, f"Successfully deleted forecast for date {date}"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="demand_forecast",
                action="delete_forecast",
                description=f"Error deleting forecast for date {date}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error deleting forecast: {str(e)}"
            