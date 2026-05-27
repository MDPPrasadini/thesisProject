# AI Lecture Search

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root directory and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Run the backend server:

```bash
uvicorn backend.app:app --reload
```

Open `frontend/index.html` in your browser.