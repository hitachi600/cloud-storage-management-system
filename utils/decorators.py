"""
Authentication Decorators for Protected Routes.
"""

from functools import wraps
from flask import session, jsonify, redirect, url_for, request


def login_required(f):
    """
    Decorator for protecting HTML page views.
    Redirects to the login page if the user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('pages.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """
    Decorator for protecting REST API endpoints.
    Returns HTTP 401 JSON response if the user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required. Please log in to access this resource.'
            }), 401
        return f(*args, **kwargs)
    return decorated_function
