"""
Page Rendering Routes.
Serves frontend HTML templates and manages navigation state.
"""

from flask import Blueprint, render_template, redirect, url_for, session, current_app
from utils.decorators import login_required
from services.auth_service import AuthService

page_bp = Blueprint('pages', __name__)


@page_bp.route('/')
def home():
    """Landing Home Page."""
    if 'user_id' in session:
        return redirect(url_for('pages.dashboard_page'))
    return render_template('index.html')


@page_bp.route('/register')
def register_page():
    """User Registration Page."""
    if 'user_id' in session:
        return redirect(url_for('pages.dashboard_page'))
    return render_template('register.html')


@page_bp.route('/login')
def login_page():
    """User Login Page."""
    if 'user_id' in session:
        return redirect(url_for('pages.dashboard_page'))
    return render_template('login.html')


@page_bp.route('/dashboard')
@login_required
def dashboard_page():
    """User Analytics & Summary Dashboard."""
    return render_template(
        'dashboard.html',
        storage_mode=current_app.config.get('STORAGE_TYPE', 'local')
    )


@page_bp.route('/upload')
@login_required
def upload_page():
    """File Upload Page."""
    allowed_exts = sorted(list(current_app.config.get('ALLOWED_EXTENSIONS', set())))
    max_mb = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024) // (1024 * 1024)
    return render_template(
        'upload.html',
        allowed_extensions=allowed_exts,
        max_size_mb=max_mb,
        storage_mode=current_app.config.get('STORAGE_TYPE', 'local')
    )


@page_bp.route('/files')
@login_required
def files_page():
    """File Listing & Management Page."""
    return render_template(
        'files.html',
        storage_mode=current_app.config.get('STORAGE_TYPE', 'local')
    )


@page_bp.route('/logout')
def logout_action():
    """Log out user and redirect to home."""
    AuthService.logout_session()
    return redirect(url_for('pages.login_page'))
