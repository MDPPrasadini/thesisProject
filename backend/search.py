import json
import requests


TRANSCRIPT_PATH = "data/transcripts/transcript.json"
SAMPLE_TRANSCRIPT_PATH = "https://ai-lecture-search-api.onrender.com/samples/"

def search_transcript(data):

    print(data)
    print(SAMPLE_TRANSCRIPT_PATH + data.filename)
    if data.issample:
        transcript_file = data.filename.replace(".mp4", ".json")
        url = SAMPLE_TRANSCRIPT_PATH + transcript_file
        print("Loading sample from:", url)
        response = requests.get(url)
        segments = response.json()
    else:
        print("Loading local transcript")
        print("Absolute path:", full_path)
        print("File exists:", os.path.exists(full_path))
        if not os.path.exists(full_path):
            raise Exception(f"Transcript file not found: {full_path}")
        with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        segments = json.loads(content)

    results = []
    for s in segments:
        if data.query.lower() in s["text"].lower():
            results.append(s)
    return results
