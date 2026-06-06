import json
import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TRANSCRIPT_PATH = "data/transcripts/transcript.json"
os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)


# ===============================
# STEP 1: SPLIT AUDIO INTO CHUNKS
# ===============================
def split_audio(video_path, chunk_dir="uploads/chunks"):
    os.makedirs(chunk_dir, exist_ok=True)

    output_pattern = os.path.join(chunk_dir, "chunk_%03d.mp3")

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-b:a", "32k",
        "-f", "segment",
        "-segment_time", "600",  # 10 minutes
        "-reset_timestamps", "1",
        output_pattern
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return sorted([
        os.path.join(chunk_dir, f)
        for f in os.listdir(chunk_dir)
        if f.endswith(".mp3")
    ])


# ===============================
# STEP 2: TRANSCRIBE CHUNKS
# ===============================
def transcribe_video(video_path):
    try:
        print(f"Starting transcription: {video_path}")

        chunk_files = split_audio(video_path)

        print(f"Total chunks: {len(chunk_files)}")

        all_segments = []
        full_text = ""

        current_time = 0

        for i, chunk in enumerate(chunk_files):
            print(f"Transcribing chunk {i+1}/{len(chunk_files)}")

            with open(chunk, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

            text = transcript.text
            full_text += text + " "

            # fake segmentation with timestamps
            sentences = text.split(". ")

            for s in sentences:
                if s.strip():
                    all_segments.append({
                        "id": len(all_segments),
                        "start": current_time,
                        "text": s.strip()
                    })
                    current_time += 4

        result = {
            "full_text": full_text.strip(),
            "segments": all_segments
        }

        with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print("Transcription completed successfully.")
        return result

    except Exception as e:
        print("Transcription failed:", str(e))
        return {"full_text": "", "segments": [], "error": str(e)}