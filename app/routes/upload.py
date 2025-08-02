from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from app.utils.ffmpeg import convert_to_mp4
from app.utils.video_info import get_video_fps  # ✅ Import FPS utility

upload_bp = Blueprint('upload', __name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['POST'])
def upload_video():
    file = request.files.get('video')

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or missing file'}), 400

    # Sanitize filename
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save uploaded file
    file.save(save_path)

    # Convert .mkv to .mp4 if needed
    if file_ext == 'mkv':
        new_path = convert_to_mp4(save_path)
        if not new_path:
            return jsonify({'error': 'Failed to convert .mkv to .mp4'}), 500
        filename = os.path.basename(new_path)
        save_path = new_path  # Update for FPS extraction

    # ✅ Extract FPS using ffprobe
    fps = get_video_fps(save_path)

    # ✅ Return URL and FPS to frontend
    return jsonify({
        'url': f'/static/uploads/{filename}',
        'fps': fps
    })