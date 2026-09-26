"""
Authentication API Endpoints.
Provides user registration, login, logout, and current user profile APIs.
"""

from flask import Blueprint, request, jsonify, session
from services.auth_service import AuthService
from utils.validators import validate_registration_data, validate_login_data
from utils.decorators import api_login_required

auth_bp = Blueprint('auth_api', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    Request JSON: { "name": "...", "email": "...", "password": "...", "confirm_password": "..." }
    """
    data = request.get_json() or {}

    is_valid, err_msg = validate_registration_data(data)
    if not is_valid:
        return jsonify({'success': False, 'error': err_msg}), 400

    user, error = AuthService.register_user(
        name=data.get('name'),
        email=data.get('email'),
        password=data.get('password')
    )

    if error:
        return jsonify({'success': False, 'error': error}), 400

    # Auto login on successful registration
    AuthService.login_session(user)

    return jsonify({
        'success': True,
        'message': 'Account registered successfully!',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in an existing user.
    Request JSON: { "email": "...", "password": "..." }
    """
    data = request.get_json() or {}

    is_valid, err_msg = validate_login_data(data)
    if not is_valid:
        return jsonify({'success': False, 'error': err_msg}), 400

    user, error = AuthService.authenticate_user(
        email=data.get('email'),
        password=data.get('password')
    )

    if error:
        return jsonify({'success': False, 'error': error}), 401

    AuthService.login_session(user)

    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """
    Log out the current user session.
    """
    AuthService.logout_session()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully.'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@api_login_required
def get_current_user_profile():
    """
    Get authenticated user information.
    """
    user = AuthService.get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200
