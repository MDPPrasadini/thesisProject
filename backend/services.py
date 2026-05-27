import json
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def extract_search_ai_summary(segments, key):

    transcript_text = ""

    for seg in segments:
        transcript_text += (
            f"[{seg['start']:.2f}] {seg['text']}\n"
        )

    prompt = f"""
        Analyze this lecture transcript.

        Focus ONLY on topics related to:
        "{key}"

        For each related topic identify:

        1. Topic name

        2. Lecture summary:
        - summarize what the lecturer explained and combine:
                - lecture explanation
                - additional AI-generated explanation
                - deeper context
                - practical understanding
                - comparison with the lecture
        - explain what extra understanding AI adds

        3. Important keywords

        4. Start timestamp

        5. End timestamp

        6. Learning resources:
        - include educational links
        - tutorials
        - documentation
        - YouTube videos
        - courses

        Return ONLY valid JSON array.

        Example:

        [
        {{
            "topic": "Neural Networks",
            "lecture_summary": "Introduction to neural network layers. The lecture explains neural network layers and activation functions. Additionally, neural networks are inspired by the human brain and are used in image recognition and AI systems. The AI explanation adds practical applications and deeper conceptual understanding beyond the lecture.",
            "keywords": ["neurons", "layers"],
            "timestamp": 120,
            "endtime": 180,
            "resources": [
            {{
                "title": "Neural Networks Explained",
                "url": "https://www.youtube.com/watch?v=aircAruvnKk"
            }}
            ]
        }}
        ]

        Transcript:
        {transcript_text}
        """


    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return []
    

def extract_search_summary(segments, key):

    transcript_text = ""

    for seg in segments:
        transcript_text += (
            f"[{seg['start']:.2f}] {seg['text']}\n"
        )

    prompt = f"""
Analyze this lecture transcript.

    Focus ONLY on topics related to:
    "{key}"
    Identify:
    - Main lecture topics related to the word "{key}" 
    - Short summary for each topic
    - Important keywords
    - Start timestamp
    - End timestamp
    - Transcript in between Start timestamp and End timestamp

    Return ONLY valid JSON.

    Example:
    [
      {{
        "topic": "Neural Networks",
        "summary": "Introduction to neural networks",
        "keywords": ["neurons", "layers"],
        "timestamp": 120,
        "endtime: 150,
        transcript : "I can't share it in the PDF, yeah, absolutely. If you want to have these slides here, but this is not included yet because just like an informal Q&A..."
      }}
    ]

    Transcript:
    {transcript_text}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return []
    

def extract_topics_with_ai(segments):

    transcript_text = ""

    for seg in segments:
        transcript_text += (
            f"[{seg['start']:.2f}] {seg['text']}\n"
        )

    prompt = f"""
    Analyze this lecture transcript.

    Identify:
    - Main lecture topics
    - Short summary for each topic
    - Important keywords
    - Start timestamp
    - End timestamp
    - Transcript in between Start timestamp and End timestamp

    Return ONLY valid JSON.

    Example:
    [
      {{
        "topic": "Neural Networks",
        "summary": "Introduction to neural networks",
        "keywords": ["neurons", "layers"],
        "timestamp": 120,
        "endtime: 150,
        transcript : "I can't share it in the PDF, yeah, absolutely. If you want to have these slides here, but this is not included yet because just like an informal Q&A..."
      }}
    ]

    Transcript:
    {transcript_text}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return []