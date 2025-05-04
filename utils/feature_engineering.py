import pandas as pd

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