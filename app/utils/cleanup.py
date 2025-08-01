import os
import time
import threading

UPLOAD_FOLDER = 'static/uploads'
MAX_FILE_AGE_SECONDS = 3600  # 1 hour

def delete_old_files():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    while True:
        now = time.time()
        for filename in os.listdir(UPLOAD_FOLDER):
            path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(path):
                mtime = os.path.getmtime(path)
                if now - mtime > MAX_FILE_AGE_SECONDS:
                    try:
                        os.remove(path)
                        print(f"[CLEANUP] Deleted {filename}")
                    except Exception as e:
                        print(f"[CLEANUP ERROR] {e}")
        time.sleep(300)  # Run every 5 minutes
