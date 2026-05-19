import whisper
import json
import os
import torch

# ===============================
# CONFIG
# ===============================
TRANSCRIPT_DIR = "data/transcripts"
TRANSCRIPT_PATH = os.path.join(TRANSCRIPT_DIR, "transcript.json")

os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

# ===============================
# DEVICE SELECTION
# ===============================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading Whisper model on: {DEVICE}")

# tiny = fastest
# base = better accuracy but slower
MODEL_SIZE = "tiny"

# Load only once when backend starts
model = whisper.load_model(MODEL_SIZE, device=DEVICE)

print("Whisper model loaded successfully.")


# ===============================
# TRANSCRIBE FUNCTION
# ===============================
def transcribe_video(video_path):
    try:
        print(f"Starting transcription: {video_path}")

        result = model.transcribe(
            video_path,
            fp16=(DEVICE == "cuda")   
        )

        segments = result["segments"]

        # Save transcript
        with open(TRANSCRIPT_PATH, "w") as f:
            json.dump(segments, f, indent=2)

        print("Transcription completed.")

        return segments

    except Exception as e:
        print("Transcription failed:", str(e))
        return []