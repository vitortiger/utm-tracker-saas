import os
import sys
from datetime import timedelta

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and routes
from src.models import db

from src.routes.auth import auth_bp
from src.routes.telegram_bots import telegram_bots_bp
from src.routes.campaigns import campaigns_bp
from src.routes.webhooks import webhooks_bp
from src.routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///utm_tracker.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
    
    # Production settings
    if os.getenv('FLASK_ENV') == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if cors_origins == '*':
        CORS(app, origins="*")
    else:
        CORS(app, origins=cors_origins.split(','))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(telegram_bots_bp, url_prefix='/api/telegram-bots')
    app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'UTM Tracker SaaS',
            'version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    
    # Serve React app
    @app.route('/')
    def serve_react_app():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_react_routes(path):
        
        # Check if file exists in static folder
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        
        # Otherwise serve React app (for client-side routing)
        return send_from_directory(app.static_folder, 'index.html')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)

