import whisper
import json
import os
import torch
import subprocess

# ===============================
# CONFIG
# ===============================
TRANSCRIPT_DIR = "data/transcripts"
TRANSCRIPT_PATH = os.path.join(TRANSCRIPT_DIR, "transcript.json")

os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

# ===============================
# DEVICE SELECTION
# ===============================
DEVICE = "cpu"  # or "cuda" if available

print(f"Loading Whisper model on: {DEVICE}")

MODEL_SIZE = "tiny"
model = whisper.load_model(MODEL_SIZE, device=DEVICE)

print("Whisper model loaded successfully.")


# ===============================
# AUDIO EXTRACTION (NEW)
# ===============================
def extract_audio(video_path: str) -> str:
    """
    Convert video → audio for faster Whisper processing
    """
    audio_path = video_path + ".mp3"

    subprocess.run(
        [
            "ffmpeg",
            "-y",              # overwrite if exists
            "-i", video_path,
            "-vn",            # remove video
            "-acodec", "mp3",
            audio_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return audio_path


# ===============================
# TRANSCRIBE FUNCTION (UPDATED)
# ===============================
def transcribe_video(video_path):
    audio_path = None

    try:
        print(f"Starting transcription: {video_path}")

        # ===============================
        # NEW: CHECK IF TRANSCRIPT EXISTS
        # ===============================
        transcript_path = video_path + ".json"

        if os.path.exists(transcript_path):
            print("Using cached transcript:", transcript_path)

            with open(transcript_path, "r") as f:
                return json.load(f)

        # STEP 1: extract audio first (NEW)
        audio_path = extract_audio(video_path)

        print(f"Audio extracted: {audio_path}")

        # STEP 2: transcribe audio instead of video
        result = model.transcribe(
            audio_path,
            fp16=(DEVICE == "cuda"),
            verbose=False,
            language="en"
        )

        segments = result["segments"]

        # Save transcript
        with open(transcript_path, "w") as f:
            json.dump(segments, f, indent=2)

        print("Transcription completed.")

        return segments

    except Exception as e:
        print("Transcription failed:", str(e))
        return []

    finally:
        # STEP 3: cleanup audio file (IMPORTANT)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)