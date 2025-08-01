from flask import Blueprint, request, Response, jsonify, stream_with_context
import requests

link_bp = Blueprint('link', __name__)

@link_bp.route('/', methods=['POST'])
def use_direct_link():
    url = request.json.get('url')
    if not url or not url.startswith('http'):
        return jsonify({'error': 'Invalid URL'}), 400

    try:
        head_res = requests.head(url, allow_redirects=True, timeout=5)
        content_type = head_res.headers.get('Content-Type', '')

        if not content_type.startswith('video'):
            return jsonify({'error': 'URL does not point to a video'}), 400

        estimated_fps = 25  # Optional placeholder
        proxy_url = f'/api/link/stream?src={url}'

        return jsonify({
            'url': proxy_url,
            'fps': estimated_fps
        })

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to validate URL: {str(e)}'}), 400


@link_bp.route('/stream')
def proxy_video():
    url = request.args.get('src')
    if not url or not url.startswith('http'):
        return 'Missing or invalid src', 400

    try:
        headers = {}
        if 'Range' in request.headers:
            headers['Range'] = request.headers['Range']
        if 'User-Agent' in request.headers:
            headers['User-Agent'] = request.headers['User-Agent']

        upstream = requests.get(url, stream=True, headers=headers, timeout=10)

        def generate():
            for chunk in upstream.iter_content(chunk_size=8192):
                yield chunk

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = {
            key: value for key, value in upstream.headers.items()
            if key.lower() not in excluded_headers
        }

        return Response(
            stream_with_context(generate()),
            status=upstream.status_code,
            headers=response_headers,
            content_type=upstream.headers.get('Content-Type', 'video/mp4')
        )
    except Exception as e:
        return f"Error proxying video: {e}", 500
