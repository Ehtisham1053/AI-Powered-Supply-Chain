import pandas as pd
from datetime import datetime
from models import db
from models.sales import Sale
from models.inventory import Inventory
from models.logs import Log

class SalesService:
    @staticmethod
    def get_sales_data():
        """Fetch sales data from the database"""
        try:
            sales = Sale.query.all()
            
            if not sales:
                return None, "No sales data found"
            
            # Convert to DataFrame
            data = []
            for sale in sales:
                data.append({
                    'Date': sale.date,
                    'Store': sale.store,
                    'Item': sale.item,
                    'Sale': sale.sale
                })
            
            df = pd.DataFrame(data)
            return df, None
        except Exception as e:
            return None, f"Error fetching sales data: {str(e)}"
    
    @staticmethod
    def add_sale(date, store, item, sale_amount, user_id=None):
        """Add a new sale record and update inventory"""
        try:
            # Check if inventory has enough stock
            inventory = Inventory.query.filter_by(store=store, item=item).first()
            
            if not inventory or inventory.stock_available < sale_amount:
                # Log the error
                log = Log(
                    user_id=user_id,
                    module="sales",
                    action="add_sale",
                    description=f"Insufficient stock for Store {store}, Item {item}",
                    status="error"
                )
                db.session.add(log)
                db.session.commit()
                
                return False, "Insufficient stock"
            
            # Update inventory
            inventory.stock_available -= sale_amount
            inventory.last_updated = datetime.utcnow()
            
            # Add sale record
            sale = Sale(
                date=date if isinstance(date, datetime) else datetime.strptime(date, '%Y-%m-%d').date(),
                store=store,
                item=item,
                sale=sale_amount
            )
            db.session.add(sale)
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="sales",
                action="add_sale",
                description=f"Added sale for Store {store}, Item {item}: {sale_amount}",
                status="success"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, "Sale added successfully"
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="sales",
                action="add_sale",
                description=f"Error adding sale for Store {store}, Item {item}: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error adding sale: {str(e)}"
    
    @staticmethod
    def import_sales_from_csv(csv_file, user_id=None):
        """Import sales data from a CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Validate columns
            required_columns = ['Date', 'Store', 'Item', 'Sale']
            for col in required_columns:
                if col not in df.columns:
                    return False, f"Missing required column: {col}"
            
            # Convert Date to datetime
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            
            # Process each row
            success_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                # Check if inventory has enough stock
                inventory = Inventory.query.filter_by(store=row['Store'], item=row['Item']).first()
                
                if not inventory or inventory.stock_available < row['Sale']:
                    # Log the error
                    log = Log(
                        user_id=user_id,
                        module="sales",
                        action="import_sales",
                        description=f"Insufficient stock for Store {row['Store']}, Item {row['Item']}",
                        status="error"
                    )
                    db.session.add(log)
                    error_count += 1
                    continue
                
                # Update inventory
                inventory.stock_available -= row['Sale']
                inventory.last_updated = datetime.utcnow()
                
                # Add sale record
                sale = Sale(
                    date=row['Date'],
                    store=row['Store'],
                    item=row['Item'],
                    sale=row['Sale']
                )
                db.session.add(sale)
                success_count += 1
            
            # Log the action
            log = Log(
                user_id=user_id,
                module="sales",
                action="import_sales",
                description=f"Imported {success_count} sales from CSV. {error_count} errors.",
                status="success" if error_count == 0 else "warning"
            )
            db.session.add(log)
            db.session.commit()
            
            return True, f"Imported {success_count} sales successfully. {error_count} errors."
        except Exception as e:
            db.session.rollback()
            
            # Log the error
            log = Log(
                user_id=user_id,
                module="sales",
                action="import_sales",
                description=f"Error importing sales from CSV: {str(e)}",
                status="error"
            )
            db.session.add(log)
            db.session.commit()
            
            return False, f"Error importing sales: {str(e)}"