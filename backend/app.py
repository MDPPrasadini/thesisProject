from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os

from .transcribe import transcribe_video
from .search import search_transcript
from .downloader import download_video
from .services import extract_topics_with_ai, extract_search_summary, extract_search_ai_summary
from fastapi.staticfiles import StaticFiles

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

# ===================== SAMPLE FILES =====================
app.mount("/samples", StaticFiles(directory="samples"), name="samples")

# ===== MODELS =====
class UrlRequest(BaseModel):
    url: str

class SearchRequest(BaseModel):
    query: str

class SummaryRequest(BaseModel):
    segments: list

class SearchSummaryRequest(BaseModel):
    segments: list
    query: str

class SearchAISummaryRequest(BaseModel):
    segments: list
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

# ===== GET SUMMARY =====
@app.post("/summary")
async def get_summary(data: SummaryRequest):
    try:
        result = extract_topics_with_ai(data.segments)
        return {
            "status": "success",
            "results": result
        }

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return {
            "status": "error",
            "message": "Failed to generate summary"
        }
    
# ===== GET SUMMARY =====
@app.post("/search-summary")
async def get_search_summary(data: SearchSummaryRequest):
    try:
        result = extract_search_summary(data.segments, data.query)
        return {
            "status": "success",
            "results": result
        }

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return {
            "status": "error",
            "message": "Failed to generate summary"
        }
    
# ===== GET SUMMARY =====
@app.post("/search-ai-summary")
async def get_search_ai_summary(data: SearchAISummaryRequest):
    try:
        result = extract_search_ai_summary(data.segments, data.query)
        return {
            "status": "success",
            "results": result
        }

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return {
            "status": "error",
            "message": "Failed to generate summary"
        }
    
    # ===================== SAMPLE LIST API =====================
@app.get("/samples")
def get_samples():
    return {
        "samples": [
            {
                "id": "lec1",
                "title": "Neural Networks Intro",
                "video": "/samples/lec1.mp4",
                "transcript": "/samples/lec1.json"
            },
            {
                "id": "lec2",
                "title": "Operating Systems Basics",
                "video": "/samples/lec2.mp4",
                "transcript": "/samples/lec2.json"
            },
            {
                "id": "lec3",
                "title": "Data Structures",
                "video": "/samples/lec3.mp4",
                "transcript": "/samples/lec3.json"
            }
        ]
    }
@app.post("/sample-transcribe")
async def sample_transcribe(data: UrlRequest):
    file_path = data.url.replace("https://thesisproject-7om6.onrender.com/", "")
    transcript = transcribe_video(file_path)

    return {
        "status": "success",
        "transcript": transcript
    }
