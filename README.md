<img width="3188" height="1202" alt="frame (3)" src="https://github.com/user-attachments/assets/517ad8e9-ad22-457d-9538-a9e62d137cd7" />


#  Click n Play 🎯


## Basic Details
### Team Name: Jäger


### Team Members
- **Team Lead:** Aswan A - TKM College of Engineering, Kollam  
- **Member 2:** Prabhath VP - TKM College of Engineering, Kollam  


###  Project Description

**Click n Play** is a hilariously impractical video player where the video plays only as long as you keep clicking — stop clicking, and it pauses. The faster you click, the smoother it plays.

It supports:
- 🔗 **YouTube URLs** — Paste a link and stream directly.
- 🌐 **Direct Video Links** — Enter a URL pointing to a video file.
- 📁 **Local File Uploads** — Upload and play your own videos one click at a time.

No autoplay, no controls — just pure chaotic precision.


### The Problem (that doesn't exist)

Ever felt that modern video players are *too convenient*? With their smooth playback, autoplay, and pause buttons, it's just too easy to watch a video from start to finish without effort. Where’s the challenge? Where’s the physical exertion?

We realized what the world *truly* needed was a video player that requires continuous manual effort — one that makes you *earn* every frame you watch.


### The Solution (that nobody asked for)

Introducing **Click n Play** — a video player that flips convenience on its head. No autoplay. No timeline scrubbing. No fancy controls. Just a button that plays one frame every time you click.

Want to watch an entire movie? Start clicking. Want it to pause? Simply stop clicking. Whether you upload a video, paste a YouTube link, or drop a direct video URL — everything runs on your clicks. It’s absurdly simple and needlessly difficult, just the way nobody wanted.

## Technical Details
### Technologies/Components Used

For Software:
- Languages: Python, JavaScript, HTML, CSS  
- Backend Framework: Flask  
- Libraries:  
  - `yt-dlp` for YouTube downloads  
  - `ffmpeg`/`ffprobe` for media metadata  
  - `requests` for URL proxying  
  - `flask_cors` for API access  
- Frontend: 
  - Canvas API for playback  
  - Custom UI toggling between upload, URL, or YouTube mode

### Implementation
For Software:
####  Backend (Flask)

- The backend is built using **Flask**, and serves APIs for:
  - Uploading and streaming local video files.
  - Accepting direct video links (e.g., `.mp4`) and proxy-streaming them.
  - Downloading and playing YouTube videos via `yt-dlp`.
- FPS and duration are extracted using `ffprobe`.
- Temporary video files are managed and cleaned periodically.
- All responses are CORS-enabled for cross-origin frontend communication.

#### Frontend (HTML + JS)

- Built using plain HTML, JavaScript, and `<canvas>` for rendering video.
- Users can select from three modes:
  - **Upload**: Choose a local video file to preview.
  - **Link**: Paste a direct video URL (e.g., from CDN or public video).
  - **YouTube**: Paste a YouTube link; it gets downloaded and played.
- Once loaded, videos don’t autoplay.
  - You must **keep clicking** to play the video frame-by-frame.
  - Stop clicking? The video freezes—like a slideshow powered by your finger.
- A **"Remove File"** button appears once a file is selected, letting users clear the canvas and reset the state.

#### Libraries Used

- `Flask` – for the backend server.
- `yt-dlp` – for downloading YouTube videos.
- `ffmpeg/ffprobe` – for extracting video metadata (FPS, duration).
- `requests` – for handling direct video URL validation and proxying.
- Vanilla JS – for frontend logic and canvas frame drawing.
  
# Installation

```bash
git clone https://github.com/yourusername/clicknplay.git
cd clicknplay
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
# Run
```bash
python run.py
```
```bash 
http://127.0.0.1:5000
```

### Project Documentation
For Software:

# Screenshots
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/41ed2aff-f0a7-4f4f-85ec-b74c8ed6d35c" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/f3db160c-1b90-4257-bdb4-64e0f42efb77" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/af9c182f-90e3-4ebd-902b-d87841a2a88f" />

### Project Demo
# Video: [link](https://drive.google.com/file/d/1W__nnwuYYna_HzjxLen9qG4AL4qD_lyy/view?usp=sharing)
  



## Team Contributions
- Aswan A:
  - Sole developer and contributor for both frontend and backend.  
  - Implemented Flask backend for video upload, YouTube download, and direct link streaming.  
  - Built the frontend with a custom click-to-play video interface using JavaScript and canvas.  
  - Integrated `yt-dlp`, `ffmpeg`, and handled metadata extraction and cleanup logic.  
  - Designed the overall project workflow and wrote the complete documentation.
- Prabhath VP:
  - [Absent during development period]

---

Made with ❤️ at TinkerHub Useless Projects 

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--25-25?link=https%3A%2F%2Fwww.tinkerhub.org%2Fevents%2FQ2Q1TQKX6Q%2FUseless%2520Projects)






