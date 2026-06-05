import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

client = OpenAI(api_key=api_key)

# ===============================
# TRANSCRIBE FUNCTION (API VERSION)
# ===============================
def transcribe_video(video_path):
    try:
        print(f"Starting transcription (OpenAI API): {video_path}")

        with open(video_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",   # or "gpt-4o-mini-transcribe"
                file=audio_file
            )

        text = transcript.text

        result = {
            "text": text
        }

        # Save transcript
        with open(TRANSCRIPT_PATH, "w") as f:
            json.dump(result, f, indent=2)

        print("Transcription completed.")

        return result

    except Exception as e:
        print("Transcription failed:", str(e))
        return {"text": "", "error": str(e)}