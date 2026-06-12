import json
import requests
import os

SAMPLE_TRANSCRIPT_PATH = "https://ai-lecture-search-api.onrender.com/samples/"
TRANSCRIPT_PATH = "uploads/"

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
        transcript_path = os.path.join(
            TRANSCRIPT_PATH,
            data.filename + ".json"
        )
        print("Loading local transcript:", transcript_path)

        if not os.path.exists(transcript_path):
            raise Exception(f"Transcript file not found: {transcript_path}")

        with open(transcript_path, "r", encoding="utf-8") as f:
            segments = json.load(f)

    results = []
    for s in segments:
        if data.query.lower() in s["text"].lower():
            results.append(s)
    return results
