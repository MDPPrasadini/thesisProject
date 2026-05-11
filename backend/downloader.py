import yt_dlp
import os
import uuid


def download_video(url: str):
    os.makedirs("uploads", exist_ok=True)

    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join("uploads", filename)

    ydl_opts = {
        "format": "best",
        "outtmpl": filepath,
        "quiet": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filepath