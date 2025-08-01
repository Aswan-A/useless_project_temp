from flask import Blueprint, request, Response, jsonify
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

        # FPS estimation placeholder
        estimated_fps = 25

        # Respond with your server's proxy endpoint instead of direct URL
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
    if not url:
        return 'Missing src', 400

    def generate():
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

    return Response(generate(), content_type='video/mp4')
