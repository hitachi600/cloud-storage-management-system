"""
File Management API Endpoints.
Handles file uploads, listing, details, downloads, and deletions.
"""

from flask import Blueprint, request, jsonify, session, current_app, redirect
from database import db
from models.file import FileRecord
from services.storage_service import get_storage_service
from utils.validators import allowed_file, sanitize_filename, get_file_extension
from utils.decorators import api_login_required

file_bp = Blueprint('file_api', __name__)


@file_bp.route('/upload', methods=['POST'])
@api_login_required
def upload_file():
    """
    Upload a file for the authenticated user.
    Expects multipart/form-data with key 'file'.
    """
    user_id = session.get('user_id')

    # Check if the file part is present in request
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file field in upload request'}), 400

    file = request.files['file']

    # Check if user selected an empty file / no file
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected for upload'}), 400

    # Validate file extension
    allowed_exts = current_app.config.get('ALLOWED_EXTENSIONS', set())
    if not allowed_file(file.filename, allowed_exts):
        return jsonify({
            'success': False,
            'error': f"File type not allowed. Supported formats: {', '.join(sorted(allowed_exts))}"
        }), 400

    # Sanitize and generate unique stored filename
    original_name, stored_name = sanitize_filename(file.filename)
    file_type = get_file_extension(original_name)

    # Save physical file using the configured storage service (Local or AWS S3)
    storage_service = get_storage_service(current_app)
    try:
        storage_meta = storage_service.save_file(
            file_storage=file,
            stored_filename=stored_name,
            user_id=user_id
        )
    except Exception as e:
        current_app.logger.error(f"Failed to upload file to storage: {e}")
        return jsonify({
            'success': False,
            'error': f"Storage upload failed: {str(e)}"
        }), 500

    # Create and persist database record
    file_record = FileRecord(
        user_id=user_id,
        original_filename=original_name,
        stored_filename=stored_name,
        file_type=file_type,
        file_size=storage_meta['file_size'],
        s3_key=storage_meta['s3_key'],
        storage_type=storage_meta['storage_type']
    )

    try:
        db.session.add(file_record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Clean up uploaded storage if db commit fails
        storage_service.delete_file(file_record)
        return jsonify({
            'success': False,
            'error': f"Database error saving file record: {str(e)}"
        }), 500

    return jsonify({
        'success': True,
        'message': f"File '{original_name}' uploaded successfully!",
        'file': file_record.to_dict()
    }), 201


@file_bp.route('/files', methods=['GET'])
@api_login_required
def list_files():
    """
    Get all uploaded files for the logged-in user.
    Optional query parameters:
      - search: filter by filename
      - type: filter by file extension/type
    """
    user_id = session.get('user_id')
    search_query = request.args.get('search', '').strip().lower()
    type_filter = request.args.get('type', '').strip().lower()

    query = FileRecord.query.filter_by(user_id=user_id)

    if search_query:
        query = query.filter(FileRecord.original_filename.ilike(f"%{search_query}%"))

    if type_filter and type_filter != 'all':
        query = query.filter(FileRecord.file_type == type_filter)

    # Order newest first
    files = query.order_by(FileRecord.uploaded_at.desc()).all()

    return jsonify({
        'success': True,
        'count': len(files),
        'files': [f.to_dict() for f in files]
    }), 200


@file_bp.route('/files/<int:file_id>', methods=['GET'])
@api_login_required
def get_file_details(file_id: int):
    """
    Get details of a specific file.
    Ensures user can only access their own files.
    """
    user_id = session.get('user_id')
    file_record = FileRecord.query.filter_by(id=file_id, user_id=user_id).first()

    if not file_record:
        return jsonify({'success': False, 'error': 'File not found or unauthorized access'}), 404

    return jsonify({
        'success': True,
        'file': file_record.to_dict()
    }), 200


@file_bp.route('/download/<int:file_id>', methods=['GET'])
@api_login_required
def download_file(file_id: int):
    """
    Download a file.
    For local storage: streams the file directly with appropriate headers.
    For S3 storage: redirects to a secure time-limited presigned S3 URL.
    """
    user_id = session.get('user_id')
    file_record = FileRecord.query.filter_by(id=file_id, user_id=user_id).first()

    if not file_record:
        return jsonify({'success': False, 'error': 'File not found or unauthorized access'}), 404

    storage_service = get_storage_service(current_app)
    result = storage_service.get_file(file_record)

    if result is None:
        return jsonify({'success': False, 'error': 'Physical file could not be found on storage'}), 404

    # If result is a URL string (S3 presigned URL), redirect to it
    if isinstance(result, str):
        return redirect(result)

    # Otherwise result is a Flask Response / send_file
    return result


@file_bp.route('/files/<int:file_id>', methods=['DELETE'])
@api_login_required
def delete_file(file_id: int):
    """
    Delete a file from database and storage.
    Ensures user can only delete their own files.
    """
    user_id = session.get('user_id')
    file_record = FileRecord.query.filter_by(id=file_id, user_id=user_id).first()

    if not file_record:
        return jsonify({'success': False, 'error': 'File not found or unauthorized access'}), 404

    # Delete physical file from storage provider
    storage_service = get_storage_service(current_app)
    deleted_physical = storage_service.delete_file(file_record)
    if not deleted_physical:
        current_app.logger.warning(f"Could not remove physical storage file for file_id {file_id}")

    # Remove database record
    try:
        db.session.delete(file_record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f"Failed to delete database record: {str(e)}"}), 500

    return jsonify({
        'success': True,
        'message': f"File '{file_record.original_filename}' deleted successfully."
    }), 200
