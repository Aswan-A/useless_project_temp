import subprocess
import os

def convert_to_mp4(input_path):
    output_path = input_path.rsplit('.', 1)[0] + '.mp4'
    try:
        subprocess.run(['ffmpeg', '-i', input_path, '-y', output_path], check=True)
        os.remove(input_path)  # Clean up original .mkv
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[FFMPEG ERROR] {e}")
        return None
