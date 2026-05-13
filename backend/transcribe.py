import whisper, json, os

model = whisper.load_model("tiny")
TRANSCRIPT_PATH = "data/transcripts/transcript.json"
os.makedirs("data/transcripts", exist_ok=True)

def transcribe_video(video_path):
    result = model.transcribe(video_path)
    segments = result["segments"]
    with open(TRANSCRIPT_PATH, "w") as f:
        json.dump(segments, f)
    return segments
