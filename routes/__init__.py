"""
Routes Package.
Registers blueprints for page routing, authentication APIs, file APIs, and dashboard APIs.
"""

from flask import Flask


def register_blueprints(app: Flask):
    """Register all application blueprints with the Flask instance."""
    from routes.page_routes import page_bp
    from routes.auth_routes import auth_bp
    from routes.file_routes import file_bp
    from routes.dashboard_routes import dashboard_bp

    app.register_blueprint(page_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(file_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
