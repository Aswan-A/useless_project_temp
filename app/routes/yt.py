from flask import Blueprint, request, jsonify, send_file, abort, current_app
import subprocess
import os
import uuid
import re
from datetime import timedelta
import mimetypes

yt_bp = Blueprint('yt', __name__)
TEMP_FOLDER = 'static/temp'
os.makedirs(TEMP_FOLDER, exist_ok=True)

def extract_video_id(url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))  # Convert seconds to HH:MM:SS

@yt_bp.route('/', methods=['POST'])
def fetch_youtube_clip():
    data = request.get_json()
    url = data.get('url', '')
    start = data.get('start', '00:00:00')  # Format: HH:MM:SS
    duration = int(data.get('duration', 30))  # Duration in seconds

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        # File paths
        base_filename = f'{video_id}_{uuid.uuid4()}'
        full_path = os.path.join(TEMP_FOLDER, base_filename + '_full.mp4')
        trimmed_path = os.path.join(TEMP_FOLDER, base_filename + '_clip.mp4')
        trimmed_audio_path = os.path.join(TEMP_FOLDER, base_filename + '_audio.wav')

        # Download full video with audio
        subprocess.run([
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            '--merge-output-format', 'mp4',
            '--quiet',
            '--no-warnings',
            '-o', full_path,
            url
        ], check=True)

        # Trim clip with ffmpeg
        subprocess.run([
            'ffmpeg',
            '-i', full_path,
            '-ss', start,
            '-t', str(duration),
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-y',
            trimmed_path
        ], check=True)

        # Extract audio from trimmed video
        subprocess.run([
            'ffmpeg',
            '-i', trimmed_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            '-y',
            trimmed_audio_path
        ], check=True)

        # Get FPS
        result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=r_frame_rate',
            '-of', 'default=nokey=1:noprint_wrappers=1',
            trimmed_path
        ], capture_output=True, text=True)

        fps_str = result.stdout.strip()
        if '/' in fps_str:
            num, denom = map(int, fps_str.split('/'))
            fps = round(num / denom, 2)
        else:
            fps = float(fps_str)

        # Get clip duration
        dur_result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=nokey=1:noprint_wrappers=1',
            trimmed_path
        ], capture_output=True, text=True)
        clip_duration = round(float(dur_result.stdout.strip()), 2)

        return jsonify({
            'url': f'/api/yt/stream?src={trimmed_path}',
            'audio': f'/api/yt/stream?src={trimmed_audio_path}',
            'fps': fps,
            'duration': clip_duration
        })

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Download or processing failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@yt_bp.route('/stream')
def stream_file():
    rel_path = request.args.get('src', '')
    rel_path = os.path.normpath(rel_path)

    if not rel_path.startswith('static/temp/') or '..' in rel_path:
        abort(400, description="Invalid or missing 'src' parameter")

    abs_path = os.path.abspath(os.path.join(current_app.root_path, '..', rel_path))
    if not os.path.exists(abs_path):
        abort(404, description="File not found")

    mime_type, _ = mimetypes.guess_type(abs_path)
    return send_file(abs_path, mimetype=mime_type or 'application/octet-stream')
