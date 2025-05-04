from models import db
from models.sales import Sale, Forecasted7Days  
from models.inventory import Inventory
from models.warehouse import Warehouse
from models.supplier import Supplier
from models.user import User
from werkzeug.security import generate_password_hash
import pandas as pd
from datetime import datetime, timedelta
import random

def initialize_database():
    """Initialize the database with sample data"""
    # Create tables
    db.create_all()
    
    # Check if database is already initialized
    if User.query.first():
        return "Database already initialized"
    
    # Create default users
    users = [
        {
            'username': 'supply_chain_manager',
            'email': 'scm@example.com',
            'password': 'password123',
            'role': 'supply_chain_manager'
        },
        {
            'username': 'warehouse_team',
            'email': 'warehouse@example.com',
            'password': 'password123',
            'role': 'warehouse_team'
        },
        {
            'username': 'procurement_officer',
            'email': 'procurement@example.com',
            'password': 'password123',
            'role': 'procurement_officer'
        },
        {
            'username': 'sales_officer',
            'email': 'sales@example.com',
            'password': 'password123',
            'role': 'sales_officer'
        }
    ]
    
    for user_data in users:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            role=user_data['role']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
    
    # Create sample suppliers
    suppliers = [
        {
            'supplier_id': 1001,
            'on_time_delivery_rate': 95.5,
            'order_accuracy_rate': 98.2,
            'lead_time': 3.5,
            'fulfillment_rate': 97.8,
            'defect_rate': 1.2,
            'return_rate': 2.5,
            'unit_price': 45.0,
            'responsiveness_score': 8.5,
            'flexibility_rating': 7.8,
            'years_in_business': 12.0,
            'customer_satisfaction_rating': 8.7
        },
        {
            'supplier_id': 1002,
            'on_time_delivery_rate': 92.1,
            'order_accuracy_rate': 96.5,
            'lead_time': 4.2,
            'fulfillment_rate': 95.3,
            'defect_rate': 2.1,
            'return_rate': 3.2,
            'unit_price': 42.5,
            'responsiveness_score': 7.9,
            'flexibility_rating': 8.2,
            'years_in_business': 8.0,
            'customer_satisfaction_rating': 8.1
        },
        {
            'supplier_id': 1003,
            'on_time_delivery_rate': 97.8,
            'order_accuracy_rate': 99.1,
            'lead_time': 2.8,
            'fulfillment_rate': 98.5,
            'defect_rate': 0.8,
            'return_rate': 1.5,
            'unit_price': 48.0,
            'responsiveness_score': 9.2,
            'flexibility_rating': 8.5,
            'years_in_business': 15.0,
            'customer_satisfaction_rating': 9.3
        }
    ]
    
    for supplier_data in suppliers:
        supplier = Supplier(**supplier_data)
        db.session.add(supplier)
        
        # Create supplier user
        supplier_user = User(
            username=f"supplier_{supplier_data['supplier_id']}",
            email=f"supplier{supplier_data['supplier_id']}@example.com",
            role='supplier',
            supplier_id=supplier_data['supplier_id']
        )
        supplier_user.set_password('password123')
        db.session.add(supplier_user)
    
    # Create sample inventory data
    for store in range(1, 11):  # 10 stores
        for item in range(1, 51):  # 50 items
            inventory = Inventory(
                store=store,
                item=item,
                stock_available=random.randint(50, 200)
            )
            db.session.add(inventory)
    
    # Create sample warehouse data
    for item in range(1, 51):  # 50 items
        warehouse = Warehouse(
            item=item,
            stock=random.randint(200, 500)
        )
        db.session.add(warehouse)
    
    # Create sample sales data
    today = datetime.now().date()
    
    # Generate sales for the past 90 days
    for day in range(90):
        date = today - timedelta(days=day)
        
        for store in range(1, 11):  # 10 stores
            for item in range(1, 51):  # 50 items
                # Not every store sells every item every day
                if random.random() < 0.7:  # 70% chance of a sale
                    
                    
                    sale = Sale(
                        date=date,
                        store=store,
                        item=item,
                        sale=random.randint(1, 20)
                    )
                    db.session.add(sale)
    
    db.session.commit()
    
    return "Database initialized with sample data"