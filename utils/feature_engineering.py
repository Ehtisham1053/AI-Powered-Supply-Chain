import pandas as pd
from tqdm import tqdm
import os
import joblib
def load_and_preprocess(df):

    df['date'] = pd.to_datetime(df['date'])
    df['sales'] = df['sales'].fillna(0)
    df = df.sort_values(by=['store', 'item', 'date']).reset_index(drop=True)
    return df

def add_sales_timeseries_metrics(df):
    df['sales_1_day_ago'] = df.groupby(['store', 'item'])['sales'].shift(1)
    df['sales_7_days_ago'] = df.groupby(['store', 'item'])['sales'].shift(7)
    df['rolling_14_day_sales'] = df.groupby(['store', 'item'])['sales'].rolling(window=14, min_periods=1).sum().reset_index(drop=True)
    df['rolling_28_day_sales'] = df.groupby(['store', 'item'])['sales'].rolling(window=28, min_periods=1).sum().reset_index(drop=True)
    df['mean_sales'] = df.groupby(['store', 'item'])['sales'].expanding().mean().reset_index(drop=True)
    return df

def add_date_features(df):
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['day_of_week'] = df['date'].dt.weekday
    df['weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['quarter'] = df['date'].dt.quarter
    return df


def create_targets(df):
    df['target_7_day_sales'] = df.groupby(['store', 'item'])['sales'].shift(-1).rolling(window=7, min_periods=1).sum().reset_index(drop=True)
    df['target_30_day_sales'] = df.groupby(['store', 'item'])['sales'].shift(-1).rolling(window=30, min_periods=1).sum().reset_index(drop=True)
    return df



def forecast_future_30(df, target_col, forecast_days=30, model_dir='ml_models/models_30'):
    """
    Forecasts total sales for each item across all stores for the next 30 days.

    Args:
        df (pd.DataFrame): Preprocessed sales data.
        target_col (str): Target column name (e.g., 'target_30_day_sales').
        forecast_days (int): Number of days to forecast.
        model_dir (str): Directory containing the trained models.

    Returns:
        pd.DataFrame: item, total_predicted_sales
    """
    df = add_sales_timeseries_metrics(df)
    df = add_date_features(df)

    features = [
        'sales_1_day_ago', 'sales_7_days_ago', 'rolling_14_day_sales',
        'rolling_28_day_sales', 'mean_sales', 'day', 'month', 'year',
        'day_of_week', 'weekend', 'quarter'
    ]

    total_results = []  # This will store the total forecast for each item
    items = df['item'].unique()
    stores = df['store'].unique()

    for item_id in tqdm(items, desc="Forecasting Items"):
        item_total_forecast = 0  # Initialize total sum for this item across all stores

        for store_id in stores:
            df_is = df[(df['item'] == item_id) & (df['store'] == store_id)].copy()
            df_is = df_is.dropna(subset=features)

            if df_is.shape[0] < forecast_days:
                continue

            X_forecast = df_is[features].tail(forecast_days)

            model_path = os.path.join(model_dir, f"{store_id}_{item_id}_{target_col}.pkl")
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                preds = model.predict(X_forecast)

                item_total_forecast += preds.sum()  # Sum 30-day predictions
            else:
                print(f"⚠️ Model missing for Store {store_id}, Item {item_id}")

        total_results.append({
            'item': item_id,
            'total_predicted_sales': item_total_forecast
        })

    return pd.DataFrame(total_results)