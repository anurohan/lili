# Lili AI Chat

Lili is a small browser-based chat application backed by a local Ollama model. The FastAPI endpoint streams generated text to the browser, keeps a short conversation context in memory, and appends completed conversations to a local log file.

## Features

- Local inference through Ollama using `llama3.1:8b`.
- Streaming responses from the `/chat` endpoint.
- A system prompt that guides Lili toward a friendly, professional Hindi/Hinglish tone.
- Up to the last 10 user/assistant messages retained as in-memory context for follow-up questions.
- Conversation entries appended to `conversation_log.txt`.
- A lightweight HTML, CSS, and JavaScript chat interface.

## Technology

- Python and FastAPI for the HTTP API.
- Ollama for local language-model inference.
- HTML, CSS, and JavaScript for the browser UI.

## Current setup limitation

The checked-in layout needs to be reconciled before the supplied launcher can run from a fresh clone:

- `app.py` looks for browser files in a `frontend/` directory, but `index.html`, `script.js`, and `style.css` are currently at the repository root.
- `start_lili.bat` changes to a machine-specific `D:\lpu\sem 04\lili\backend` path; that path is not portable and does not match this repository's checked-in root layout.
- There is no dependency manifest in the repository.

These are project setup issues, not steps the README can safely fix by assuming a local machine path. Update the frontend path/launcher and add a dependency manifest before treating the one-click start as portable.

## Development prerequisites

After aligning those paths, a local development environment needs Python, Ollama, and Node-free static frontend assets. Install the `fastapi`, `uvicorn`, and `ollama` Python packages in a virtual environment, then fetch the model used by the server:

```sh
ollama pull llama3.1:8b
```

Once the FastAPI app can find its static frontend directory, start the API from the directory containing `app.py` with:

```sh
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` after the app starts. The current checked-in directory mismatch must be corrected first.

## API

### `GET /`

Serves the frontend `index.html` from the configured frontend directory.

### `POST /chat`

Accepts a JSON object containing a `message` string and streams a plain-text reply. The model call uses CPU inference settings in the current implementation. An empty message returns a short greeting.

## Privacy and limitations

Conversation text is appended to `conversation_log.txt` in plain text, and in-memory context is reset when the server restarts. Do not use sensitive messages on a shared machine, and do not publish a conversation log containing private information. The server currently configures permissive CORS; restrict allowed origins before exposing it beyond local development.