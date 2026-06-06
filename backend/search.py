import json
import os

TRANSCRIPT_PATH = "data/transcripts/transcript.json"

def search_transcript(query):
    if not os.path.exists(TRANSCRIPT_PATH):
        return []   # no crash

    with open(TRANSCRIPT_PATH, "r") as f:
        segments = json.load(f)

    results = []
    for s in segments:
        if query.lower() in s.get("text", "").lower():
            results.append(s)

    return results
