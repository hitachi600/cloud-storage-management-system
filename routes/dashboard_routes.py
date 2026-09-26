"""
Dashboard API Endpoints.
Calculates storage analytics, recent uploads, and metrics for the authenticated user.
"""

from collections import Counter
from flask import Blueprint, jsonify, session, current_app
from models.file import FileRecord
from utils.validators import format_bytes
from utils.decorators import api_login_required

dashboard_bp = Blueprint('dashboard_api', __name__)

# Standard 100 MB free quota metric for visual progress
STORAGE_QUOTA_BYTES = 100 * 1024 * 1024


@dashboard_bp.route('/dashboard', methods=['GET'])
@api_login_required
def get_dashboard_stats():
    """
    Get dashboard metrics for the logged-in user.
    Returns storage usage, total files, recent files, and file type distribution.
    """
    user_id = session.get('user_id')

    # Query all user files
    user_files = FileRecord.query.filter_by(user_id=user_id).order_by(FileRecord.uploaded_at.desc()).all()

    total_files = len(user_files)
    total_bytes = sum(f.file_size for f in user_files)
    storage_percentage = min(100.0, (total_bytes / STORAGE_QUOTA_BYTES) * 100.0) if STORAGE_QUOTA_BYTES > 0 else 0.0

    # Categorize file types
    type_counts = Counter()
    for f in user_files:
        ext = f.file_type.lower()
        if ext in ['pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx']:
            type_counts['Documents'] += 1
        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp']:
            type_counts['Images'] += 1
        elif ext in ['zip', 'tar', 'gz', 'rar', '7z']:
            type_counts['Archives'] += 1
        else:
            type_counts['Others'] += 1

    # Most recent 5 files
    recent_files = [f.to_dict() for f in user_files[:5]]

    return jsonify({
        'success': True,
        'metrics': {
            'total_files': total_files,
            'total_storage_bytes': total_bytes,
            'formatted_storage': format_bytes(total_bytes),
            'storage_quota_bytes': STORAGE_QUOTA_BYTES,
            'formatted_quota': format_bytes(STORAGE_QUOTA_BYTES),
            'storage_percentage': round(storage_percentage, 2),
            'storage_mode': current_app.config.get('STORAGE_TYPE', 'local'),
            'type_breakdown': dict(type_counts),
            'recent_files': recent_files
        }
    }), 200
