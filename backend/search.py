import json

TRANSCRIPT_PATH = "data/transcripts/transcript.json"


def search_transcript(query):
    try:
        with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        segments = data.get("segments", [])

        results = []

        for s in segments:
            text = s.get("text", "")

            if query.lower() in text.lower():
                results.append(s)

        return results

    except FileNotFoundError:
        return []

    except Exception as e:
        print("Search error:", str(e))
        return []