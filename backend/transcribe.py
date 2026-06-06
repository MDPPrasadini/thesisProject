import json
import os
import subprocess
from openai import OpenAI

# ===============================
# CONFIG
# ===============================
TRANSCRIPT_DIR = "data/transcripts"
TRANSCRIPT_PATH = os.path.join(TRANSCRIPT_DIR, "transcript.json")

os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

# ===============================
# OPENAI CLIENT
# ===============================
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Set it in Render environment variables.")

client = OpenAI(api_key=api_key)

# ===============================
# HELPERS
# ===============================
def extract_audio(video_path: str) -> str:
    """
    Convert video → audio (required to avoid OpenAI 25MB limit)
    """
    audio_path = video_path.rsplit(".", 1)[0] + ".mp3"

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ], check=True)

    return audio_path


# ===============================
# TRANSCRIBE FUNCTION
# ===============================
def transcribe_video(video_path):
    try:
        print(f"Starting transcription (OpenAI API): {video_path}")

        # 1. Convert video → audio (fixes 413 error)
        audio_path = extract_audio(video_path)

        # 2. Send audio to OpenAI Whisper API
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        text = transcript.text

        result = {
            "text": text
        }

        # 3. Save transcript locally (optional cache)
        with open(TRANSCRIPT_PATH, "w") as f:
            json.dump(result, f, indent=2)

        print("Transcription completed successfully.")

        return result

    except Exception as e:
        print("Transcription failed:", str(e))
        return {
            "text": "",
            "error": str(e)
        }
