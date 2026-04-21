#!/usr/bin/env python3
"""
app.py - Main application module
Project: Project
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Any, Dict, List

# Third-party imports
try:
    from flask import Flask, request, jsonify, render_template, abort
    from flask_cors import CORS
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install with: pip install flask flask-cors")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

class AppError(Exception):
    """Custom application exception class."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def validate_input(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate input data contains all required fields.
    
    Args:
        data: Input data dictionary
        required_fields: List of required field names
        
    Returns:
        bool: True if all required fields are present
    """
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    return True

@app.before_request
def before_request():
    """Execute before each request."""
    logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Execute after each request."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.route('/')
def index():
    """Render the main index page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return "Welcome to Project Application", 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'project-app'
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """Retrieve data endpoint."""
    try:
        # Example data retrieval
        sample_data = {
            'items': [
                {'id': 1, 'name': 'Item 1', 'value': 100},
                {'id': 2, 'name': 'Item 2', 'value': 200},
                {'id': 3, 'name': 'Item 3', 'value': 300}
            ],
            'total': 3,
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(sample_data), 200
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        return jsonify({'error': 'Failed to retrieve data'}), 500

@app.route('/api/data', methods=['POST'])
def create_data():
    """Create new data endpoint."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'value']
        if not validate_input(data, required_fields):
            return jsonify({
                'error': f'Missing required fields: {required_fields}'
            }), 400
        
        # Process data (example)
        new_item = {
            'id': len(data.get('items', [])) + 1 if 'items' in data else 1,
            'name': data['name'],
            'value': data['value'],
            'created_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Created new item: {new_item}")
        
        return jsonify({
            'message': 'Data created successfully',
            'item': new_item
        }), 201
        
    except AppError as e:
        logger.error(f"Application error: {e}")
        return jsonify({'error': e.message}), e.status_code
    except Exception as e:
        logger.error(f"Error creating data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/data/<int:item_id>', methods=['GET'])
def get_single_data(item_id: int):
    """Retrieve single data item by ID."""
    try:
        # Example data lookup
        if item_id <= 0:
            return jsonify({'error': 'Invalid item ID'}), 400
        
        # Simulate database lookup
        if item_id > 100:
            return jsonify({'error': 'Item not found'}), 404
        
        item = {
            'id': item_id,
            'name': f'Item {item_id}',
            'value': item_id * 100,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(item), 200
        
    except Exception as e:
        logger.error(f"Error retrieving item {item_id}: {e}")
        return jsonify({'error': 'Failed to retrieve item'}), 500

@app.route('/api/data/<int:item_id>', methods=['PUT'])
def update_data(item_id: int):
    """Update existing data endpoint."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'value']
        if not validate_input(data, required_fields):
            return jsonify({
                'error': f'Missing required fields: {required_fields}'
            }), 400
        
        # Check if item exists (simulated)
        if item_id > 100:
            return jsonify({'error': 'Item not found'}), 404
        
        # Update item (example)
        updated_item = {
            'id': item_id,
            'name': data['name'],
            'value': data['value'],
            'updated_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Updated item {item_id}: {updated_item}")
        
        return jsonify({
            'message': 'Data updated successfully',
            'item': updated_item
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        return jsonify({'error': 'Failed to update item'}), 500

@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_data(item_id: int):
    """Delete data endpoint."""
    try:
        # Check if item exists (simulated)
        if item_id > 100:
            return jsonify({'error': 'Item not found'}), 404
        
        logger.info(f"Deleted item {item_id}")
        
        return jsonify({
            'message': f'Item {item_id} deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        return jsonify({'error': 'Failed to delete item'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Application factory function.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Flask: Configured Flask application instance
    """
    if config:
        app.config.update(config)
    
    return app

if __name__ == '__main__':
    try:
        # Get port from environment variable or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Validate port range
        if not (1 <= port <= 65535):
            raise ValueError(f"Invalid