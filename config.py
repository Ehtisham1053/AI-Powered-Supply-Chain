import os
from datetime import timedelta

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:ehti1053@localhost/supply_chain"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Application configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = True
    
    # ML model paths
    MODELS_7_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models/models_7')
    MODELS_30_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models/models_30')
    SUPPLIER_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models/supplier_model')
    
    # Item and store mappings
    STORE_MAPPING = {
        1: "PAKMART G-9 MARKAZ",
        2: "PAKMART F-10 CENTER",
        3: "PAKMART I-8 COMMERCIAL",
        4: "PAKMART DHA PHASE 2",
        5: "PAKMART BLUE AREA",
        6: "PAKMART BAHARAKU",
        7: "PAKMART GULBERG GREENS",
        8: "PAKMART F-6 SUPER MARKET",
        9: "PAKMART BANI GALA",
        10: "PAKMART H-13 SERVICE ROAD"
    }
    
    # In config.py
    ITEM_MAPPING = {
        1: "Fresh Fruits",
        2: "Fresh Vegetables",
        3: "Dairy Products",
        4: "Meat Products",
        5: "Seafood",
        6: "Bakery Items",
        7: "Frozen Foods",
        8: "Canned Goods",
        9: "Dry Pasta",
        10: "Rice",
        11: "Breakfast Cereals",
        12: "Snacks",
        13: "Confectionery",
        14: "Beverages",
        15: "Alcoholic Drinks",
        16: "Health Foods",
        17: "Baby Products",
        18: "Pet Supplies",
        19: "Cleaning Products",
        20: "Laundry Supplies",
        21: "Paper Products",
        22: "Personal Care",
        23: "Health Care",
        24: "Beauty Products",
        25: "Kitchen Supplies",
        26: "Home Decor",
        27: "Bedding",
        28: "Bath Accessories",
        29: "Garden Supplies",
        30: "Outdoor Living",
        31: "Tools",
        32: "Hardware",
        33: "Automotive Supplies",
        34: "Electronics",
        35: "Computers",
        36: "Mobile Phones",
        37: "Audio Equipment",
        38: "TV & Video",
        39: "Gaming",
        40: "Toys",
        41: "Sports Equipment",
        42: "Fitness Gear",
        43: "Camping Gear",
        44: "Books",
        45: "Magazines",
        46: "Office Supplies",
        47: "School Supplies",
        48: "Craft Supplies",
        49: "Seasonal Items",
        50: "Gift Items"
    }
    
    # Complete the item mapping as per the document
    for i in range(3, 51):
        if i not in ITEM_MAPPING:
            ITEM_MAPPING[i] = f"Item {i}"