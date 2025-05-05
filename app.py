from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import init_db
from controllers import init_routes
from config import Config
from datetime import datetime
from utils.db_utils import initialize_database

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    

    jwt = JWTManager(app)
    init_db(app)
    
    # Initialize routes
    init_routes(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    # Database initialization route
    @app.route('/api/init-db', methods=['POST'])
    def init_db_route():
        result = initialize_database()
        return jsonify({
            'success': True,
            'message': result
        }), 200
    
    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'message': 'API is running',
            'timestamp': str(datetime.utcnow())
        }), 200
    
    return app

if __name__ == '__main__':
    from datetime import datetime
    app = create_app()
    app.run(debug=True)