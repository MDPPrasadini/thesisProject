from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os

from .transcribe import transcribe_video
from .search import search_transcript
from .downloader import download_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ===== MODELS =====
class UrlRequest(BaseModel):
    url: str


class SearchRequest(BaseModel):
    query: str


# ===== UPLOAD =====
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcript = transcribe_video(file_path)

    return {
        "status": "success",
        "message": "Transcription complete",
        "filename": file.filename,
        "transcript": transcript
    }


# ===== SEARCH (POST for frontend flexibility) =====
@app.post("/search")
def search(data: SearchRequest):
    results = search_transcript(data.query)

    return {
        "status": "success",
        "results": results
    }


# ===== DOWNLOAD + TRANSCRIBE =====
@app.post("/download-url")
async def download_from_url(data: UrlRequest):
    file_path = download_video(data.url)
    transcript = transcribe_video(file_path)

    return {
        "status": "success",
        "message": "Lecture downloaded and transcribed",
        "transcript": transcript
    }