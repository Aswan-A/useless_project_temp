from flask import Blueprint, request, jsonify, send_file ,abort, current_app
import subprocess
import os
import uuid
import re

yt_bp = Blueprint('yt', __name__)
TEMP_FOLDER = 'static/temp'
os.makedirs(TEMP_FOLDER, exist_ok=True)

def extract_video_id(url):
    # Accepts youtu.be/xxxx and youtube.com/watch?v=xxxx
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@yt_bp.route('/', methods=['POST'])
def fetch_youtube_clip():
    data = request.get_json()
    url = data.get('url', '')
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    output_path = os.path.join(TEMP_FOLDER, f'{uuid.uuid4()}.mp4')

    try:
        # Download ~10s MP4 clip (fastest stream) using yt-dlp
        subprocess.run([
            'yt-dlp',
            '-f', 'mp4',
            '--download-sections', '*00:00:00-00:00:10',
            '-o', output_path,
            url
        ], check=True)

        # Extract FPS with ffprobe
        result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=r_frame_rate',
            '-of', 'default=nokey=1:noprint_wrappers=1',
            output_path
        ], capture_output=True, text=True)

        fps_str = result.stdout.strip()
        if '/' in fps_str:
            num, denom = map(int, fps_str.split('/'))
            fps = round(num / denom, 2)
        else:
            fps = float(fps_str)

        return jsonify({
            'url': f'/api/yt/stream?src={output_path}',
            'fps': fps
        })

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@yt_bp.route('/stream')
def stream_file():
    rel_path = request.args.get('src')  # e.g., 'static/temp/xyz.mp4'
    if not rel_path or '..' in rel_path:
        abort(400, description="Invalid or missing 'src' parameter")

    # Use absolute path relative to project root (not app folder)
    abs_path = os.path.join(current_app.root_path, '..', rel_path)

    abs_path = os.path.abspath(abs_path)  # Normalize

    if not os.path.exists(abs_path):
        abort(404, description="File not found")

    return send_file(abs_path, mimetype='video/mp4')
