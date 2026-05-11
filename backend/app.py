from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil, os
from transcribe import transcribe_video
from .search import search_transcript
from .downloader import download_video
from pydantic import BaseModel

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

class UrlRequest(BaseModel):
    url: str

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcript = transcribe_video(file_path)
    return {"message": "Transcription complete", "transcript": transcript}

@app.get("/search")
def search(q: str):
    return search_transcript(q)

@app.post("/download-url")
async def download_from_url(data: UrlRequest):
    file_path = download_video(data.url)

    transcript = transcribe_video(file_path)

    return {
        "message": "Lecture downloaded and transcribed",
        "transcript": transcript
    }
