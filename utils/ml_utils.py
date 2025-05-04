import os
import joblib
import pandas as pd
import numpy as np
from config import Config

def load_model(model_path):
    """Load a machine learning model from a file"""
    try:
        model = joblib.load(model_path)
        return model, None
    except Exception as e:
        return None, f"Error loading model: {str(e)}"

def forecast_future(df, forecast_days, target_col, model_dir):
    """Forecast future sales for the specified number of days"""
    try:
        # Preprocess data
        # This is a placeholder for the actual preprocessing code
        # The real implementation would depend on the specific models and features

        # Load models from the specified directory
        if not os.path.exists(model_dir):
            return None, f"Model directory not found: {model_dir}"

        # Get unique store-item combinations (for 7-day forecast) or items (for 30-day forecast)
        if 'Store' in df.columns and target_col == 'target_7_day_sales':
            # 7-day forecast (store-item level)
            groups = df[['Store', 'Item']].drop_duplicates()
            forecast_results = pd.DataFrame(columns=['Store', 'Item', 'total_7_days_prediction'])

            for _, row in groups.iterrows():
                store = row['Store']
                item = row['Item']

                # Load model for this store-item combination
                model_path = os.path.join(model_dir, f"model_store_{store}_item_{item}.pkl")

                # If model doesn't exist, skip this combination
                if not os.path.exists(model_path):
                    continue

                # Load model
                model, error = load_model(model_path)
                if error:
                    continue

                # Filter data for this store and item
                item_data = df[(df['Store'] == store) & (df['Item'] == item)]

                if len(item_data) < 7:  # Need at least 7 days of data
                    continue

                # Prepare features for prediction
                # This is a placeholder for the actual feature preparation
                # The real implementation would depend on the specific models and features
                X = item_data[['Day', 'Month', 'Year', 'DayOfWeek', 'WeekOfYear', 'IsWeekend',
                              'Rolling_Mean_7d', 'Rolling_Max_7d', 'Rolling_Min_7d', 'Rolling_Std_7d']].values

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


            return forecast_results, None

        elif target_col == 'target_30_day_sales':
            # 30-day forecast (item level)
            items = df['Item'].unique()
            forecast_results = pd.DataFrame(columns=['Item', 'total_predicted_sales'])

            for item in items:
                # Load model for this item
                model_path = os.path.join(model_dir, f"model_item_{item}.pkl")

                # If model doesn't exist, skip this item
                if not os.path.exists(model_path):
                    continue

                # Load model
                model, error = load_model(model_path)
                if error:
                    continue

                # Filter data for this item
                item_data = df[df['Item'] == item]

                if len(item_data) < 30:  # Need at least 30 days of data
                    continue

                # Prepare features for prediction
                # This is a placeholder for the actual feature preparation
                # The real implementation would depend on the specific models and features
                X = item_data[['Day', 'Month', 'Year', 'DayOfWeek', 'WeekOfYear', 'IsWeekend',
                              'Rolling_Mean_30d', 'Rolling_Max_30d', 'Rolling_Min_30d', 'Rolling_Std_30d']].values

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



            return forecast_results, None

        else:
            return None, "Invalid target column or missing required columns"

    except Exception as e:
        return None, f"Error forecasting future sales: {str(e)}"
