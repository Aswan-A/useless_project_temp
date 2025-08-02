from flask import Blueprint, request, jsonify, send_file, abort
import subprocess
import os
import re
import logging
from flask_cors import cross_origin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

yt_bp = Blueprint('yt', __name__)

# Use absolute path for temp folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_FOLDER = os.path.join(BASE_DIR, '..', 'static', 'temp')
TEMP_FOLDER = os.path.abspath(TEMP_FOLDER)
os.makedirs(TEMP_FOLDER, exist_ok=True)

logger.info(f"Temp folder set to: {TEMP_FOLDER}")

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal and invalid characters"""
    # Remove any path separators and invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip('. ')
    return filename

@yt_bp.route('/', methods=['POST'])
@cross_origin()
def fetch_youtube_clip():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        url = data.get('url', '').strip()
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        logger.info(f"Processing URL: {url}")
        
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL format'}), 400

        logger.info(f"Extracted video ID: {video_id}")
        
        # Sanitize the video ID for filename
        safe_video_id = sanitize_filename(video_id)
        filename = f"{safe_video_id}.%(ext)s"
        
        # Use absolute path for output
        output_template = os.path.join(TEMP_FOLDER, filename)
        logger.info(f"Output template: {output_template}")
        
        # Check if file already exists (check for .mp4, .webm, .mkv extensions)
        existing_files = []
        for ext in ['mp4', 'webm', 'mkv', 'm4v']:
            potential_file = os.path.join(TEMP_FOLDER, f"{safe_video_id}.{ext}")
            if os.path.exists(potential_file):
                existing_files.append(potential_file)
        
        if existing_files:
            # Use the first existing file
            full_path = existing_files[0]
            logger.info(f"Using existing file: {full_path}")
        else:
            # Download the video
            logger.info("Starting download...")
            
            cmd = [
                'yt-dlp',
                '--format',
                'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]/best[height<=1080]',
                '--merge-output-format', 'mp4',
                '--output', output_template,
                '--no-playlist',
                '--no-warnings',
                '--quiet',
                '--embed-metadata',
                url
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=TEMP_FOLDER,  # Set working directory
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            logger.info(f"yt-dlp stdout: {result.stdout}")
            if result.stderr:
                logger.error(f"yt-dlp stderr: {result.stderr}")
            
            if result.returncode != 0:
                return jsonify({
                    'error': f'Download failed: {result.stderr or "Unknown error"}'
                }), 500
            
            # Find the downloaded file
            downloaded_files = []
            for ext in ['mp4', 'webm', 'mkv', 'm4v']:
                potential_file = os.path.join(TEMP_FOLDER, f"{safe_video_id}.{ext}")
                if os.path.exists(potential_file):
                    downloaded_files.append(potential_file)
            
            if not downloaded_files:
                # List all files in temp folder for debugging
                temp_files = os.listdir(TEMP_FOLDER)
                logger.error(f"No downloaded file found. Files in temp folder: {temp_files}")
                return jsonify({
                    'error': 'Download completed but file not found. Check server logs.'
                }), 500
            
            full_path = downloaded_files[0]
            logger.info(f"Downloaded file: {full_path}")

        # Verify file exists and get info
        if not os.path.exists(full_path):
            return jsonify({'error': 'Video file not found after download'}), 500

        file_size = os.path.getsize(full_path)
        logger.info(f"File size: {file_size} bytes")
        
        if file_size == 0:
            return jsonify({'error': 'Downloaded file is empty'}), 500

        # Get video metadata with error handling
        fps = 30.0
        duration = 0.0
        
        try:
            # Get FPS
            fps_cmd = [
                'ffprobe', '-v', 'quiet',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=r_frame_rate',
                '-of', 'csv=p=0',
                full_path
            ]
            fps_result = subprocess.run(fps_cmd, capture_output=True, text=True, timeout=30)
            if fps_result.returncode == 0 and fps_result.stdout.strip():
                fps_str = fps_result.stdout.strip()
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    fps = round(float(num) / float(den), 2) if float(den) != 0 else 30.0
                else:
                    fps = round(float(fps_str), 2)
            logger.info(f"Detected FPS: {fps}")
        except Exception as e:
            logger.warning(f"Could not get FPS: {e}")

        try:
            # Get duration
            dur_cmd = [
                'ffprobe', '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                full_path
            ]
            dur_result = subprocess.run(dur_cmd, capture_output=True, text=True, timeout=30)
            if dur_result.returncode == 0 and dur_result.stdout.strip():
                duration = round(float(dur_result.stdout.strip()), 2)
            logger.info(f"Detected duration: {duration} seconds")
        except Exception as e:
            logger.warning(f"Could not get duration: {e}")

        # Return the relative filename for streaming
        relative_filename = os.path.basename(full_path)
        
        response_data = {
            'url': f'/api/yt/stream?file={relative_filename}',
            'fps': fps,
            'duration': duration,
            'filesize': file_size
        }
        
        logger.info(f"Returning response: {response_data}")
        return jsonify(response_data)

    except subprocess.TimeoutExpired:
        logger.error("Download timed out")
        return jsonify({'error': 'Download timed out (5 minutes)'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@yt_bp.route('/stream')
@cross_origin()
def stream_video():
    try:
        filename = request.args.get('file')
        
        if not filename:
            return abort(400, 'File parameter is required')
        
        # Security check: prevent path traversal
        if '/' in filename or '\\' in filename or '..' in filename:
            logger.warning(f"Potentially malicious filename: {filename}")
            return abort(400, 'Invalid filename')
        
        # Additional security: only allow specific extensions
        allowed_extensions = ['.mp4', '.webm', '.mkv', '.m4v']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            return abort(400, 'Invalid file type')
        
        abs_path = os.path.join(TEMP_FOLDER, filename)
        logger.info(f"Attempting to serve file: {abs_path}")
        
        if not os.path.isfile(abs_path):
            logger.error(f"File not found: {abs_path}")
            # List files in temp folder for debugging
            try:
                temp_files = os.listdir(TEMP_FOLDER)
                logger.info(f"Files in temp folder: {temp_files}")
            except:
                pass
            return abort(404, 'File not found')
        
        file_size = os.path.getsize(abs_path)
        logger.info(f"Serving file {filename} ({file_size} bytes)")
        
        # Determine MIME type
        if filename.lower().endswith('.mp4'):
            mimetype = 'video/mp4'
        elif filename.lower().endswith('.webm'):
            mimetype = 'video/webm'
        elif filename.lower().endswith('.mkv'):
            mimetype = 'video/x-matroska'
        else:
            mimetype = 'video/mp4'  # default
        
        return send_file(abs_path, mimetype=mimetype, as_attachment=False)
        
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}", exc_info=True)
        return abort(500, 'Error serving file')

@yt_bp.route('/debug/files')
@cross_origin()
def debug_files():
    """Debug endpoint to list files in temp folder"""
    try:
        files = []
        for filename in os.listdir(TEMP_FOLDER):
            filepath = os.path.join(TEMP_FOLDER, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'path': filepath
                })
        
        return jsonify({
            'temp_folder': TEMP_FOLDER,
            'files': files,
            'total_files': len(files)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500