import subprocess

def get_video_fps(filepath):
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=avg_frame_rate',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            filepath
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        rate = result.stdout.strip()  # e.g., "25/1" or "30000/1001"
        if '/' in rate:
            num, denom = rate.split('/')
            return round(float(num) / float(denom), 2)
        return float(rate)
    except Exception as e:
        print(f"Error extracting FPS: {e}")
        return 25  # fallback default
