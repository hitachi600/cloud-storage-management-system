"""
Main Application Entry Point for Cloud Storage Management System.
Implements the Application Factory pattern with Flask, SQLAlchemy, and storage service configuration.
"""

import os
from flask import Flask, render_template, jsonify, session
from config import Config
from database import init_db
from routes import register_blueprints


def create_app(config_class=Config):
    """
    Create and configure an instance of the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Validate storage settings
    config_class.validate_storage_config()

    # Initialize Database
    init_db(app)

    # Register Blueprints / Routes
    register_blueprints(app)

    # Context Processor: Inject global template variables
    @app.context_processor
    def inject_global_variables():
        return {
            'app_name': 'Cloud Storage Management System',
            'current_user_name': session.get('user_name'),
            'current_user_email': session.get('user_email'),
            'is_authenticated': 'user_id' in session,
            'storage_mode': app.config.get('STORAGE_TYPE', 'local')
        }

    # Custom Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        if app.config.get('TESTING') or 'application/json' in getattr(error, 'description', ''):
            return jsonify({'success': False, 'error': 'Bad Request'}), 400
        return render_template('404.html', error_title='Bad Request (400)', error_message='The request could not be processed.'), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html', error_title='Page Not Found (404)', error_message='The page or resource you are looking for does not exist.'), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        max_mb = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024) // (1024 * 1024)
        return jsonify({
            'success': False,
            'error': f'File is too large! Maximum allowed upload size is {max_mb} MB.'
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('500.html', error_title='Internal Server Error (500)', error_message='An unexpected error occurred on the server.'), 500

    return app


# Main application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"================================================================")
    print(f" Cloud Storage Management System running at: http://127.0.0.1:{port}")
    print(f" Storage Mode: {app.config.get('STORAGE_TYPE').upper()}")
    print(f" Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"================================================================")
    app.run(host='0.0.0.0', port=port, debug=True)
