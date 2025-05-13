# controllers/__init__.py

# Import all blueprints from their respective controller files
from .auth_controller import auth_bp
from .demand_controller import demand_bp
from .inventory_controller import inventory_bp
from .message_controller import message_bp
from .warehouse_controller import warehouse_bp
from .user_controller import user_bp
from .procurement_controller import procurement_bp

from .supplier_controller import supplier_bp
from .sales_controller import sales_bp
from .supplier_dashboard_controller import supplier_dashboard_bp

from .log_controller import log_bp

from .inventory_controller import inventory_bp
def init_routes(app):
    # Register blueprints with the app
    app.register_blueprint(auth_bp)
    app.register_blueprint(demand_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(warehouse_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(supplier_dashboard_bp)


