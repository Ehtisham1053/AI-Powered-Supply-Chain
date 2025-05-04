from datetime import datetime
import pandas as pd
import numpy as np
from config import Config

def get_store_name(store_id):
    """Get the store name from the store ID"""
    return Config.STORE_MAPPING.get(store_id, f"Store {store_id}")

def get_item_name(item_id):
    """Get the item name from the item ID"""
    return Config.ITEM_MAPPING.get(item_id, f"Item {item_id}")

def generate_po_number():
    """Generate a unique purchase order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"PO-{timestamp}"

def format_currency(amount):
    """Format a number as currency"""
    return f"${amount:.2f}"

def calculate_days_of_stock(stock, daily_sales):
    """Calculate the number of days of stock remaining"""
    if daily_sales == 0:
        return float('inf')  # Infinite days if no sales
    
    return stock / daily_sales

def calculate_reorder_point(lead_time, daily_sales, safety_stock=0):
    """Calculate the reorder point based on lead time and daily sales"""
    return (lead_time * daily_sales) + safety_stock

def calculate_economic_order_quantity(annual_demand, order_cost, holding_cost):
    """Calculate the economic order quantity (EOQ)"""
    return np.sqrt((2 * annual_demand * order_cost) / holding_cost)

def validate_csv_format(file_path, required_columns):
    """Validate that a CSV file has the required columns"""
    try:
        df = pd.read_csv(file_path)
        
        # Check if all required columns are present
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        return True, None
    except Exception as e:
        return False, f"Error validating CSV format: {str(e)}"