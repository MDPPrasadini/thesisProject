import json

TRANSCRIPT_PATH = "data/transcripts/transcript.json"

def search_transcript(query):
    with open(TRANSCRIPT_PATH) as f:
        segments = json.load(f)

    results = []
    for s in segments:
        if query.lower() in s["text"].lower():
            results.append(s)
    return results
