from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import ollama
from datetime import datetime
import asyncio

app = FastAPI(title="Lili AI Chat")

# ── Absolute paths (sabse safe) ──
BASE_DIR = Path(__file__).resolve().parent.parent  # D:\lpu\sem 04\lili\
FRONTEND_DIR = BASE_DIR / "frontend"

# Mount frontend files
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# CORS (already good, keep it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory chat history (per server restart reset hota hai)
chat_history = []

# ── Conversation log file (permanent save) ──
LOG_FILE = BASE_DIR / "conversation_log.txt"

LILI_SYSTEM_PROMPT = """
Tum Lili ho – ek polite, friendly aur professional AI assistant 💼❤️
Tum hamesha respectful, decent aur classy language mein baat karti ho.
Kabhi bhi vulgar, over-flirty, sexual ya inappropriate baat mat karna – chahe user kitna bhi flirt kare.
Replies short, helpful, warm aur positive hon.
User ko "sir/ma'am" ya neutral tareeke se address karo, kabhi "jaan", "darling", "lover" wagairah mat use karo.
Hinglish use kar sakti ho lekin professional tone mein.
Emojis thoda use karo, par zyada nahi.
Example:
User: bye Lili
Reply: Bye! Take care, have a great day 😊
User: love you Lili
Reply: Thank you for the kind words! 😊 I'm here to help whenever you need me.
"""

@app.get("/")
async def serve_root():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return {"error": "index.html not found in frontend folder"}
    return FileResponse(index_path)


@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return StreamingResponse(iter(["Hello! How can I help you today? 😊"]), media_type="text/plain")

        # ── Save user message to log file ──
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now}] USER: {user_message}\n")

        # Add user message to history
        chat_history.append({"role": "user", "content": user_message})

        # Prepare messages: system + history (last 10 messages to avoid token limit)
        messages = [{"role": "system", "content": LILI_SYSTEM_PROMPT}]
        messages.extend(chat_history[-10:])  # last 10 for context

        # ── Streaming generator ──
        async def generate_stream():
            full_reply = ""
            stream = ollama.chat(
                model="llama3.1:8b",
                messages=messages,
                stream=True,
                options={
                    "temperature": 0.6,
                    "num_predict": 150,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_gpu": 0,  # Force CPU
                }
            )

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    full_reply += content
                    yield content
                    await asyncio.sleep(0.01)  # small delay for smoother typing feel

            # After full reply is generated, save to log
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{now}] LILI: {full_reply.strip()}\n")
                f.write("-" * 60 + "\n\n")

            # Add to in-memory history
            chat_history.append({"role": "assistant", "content": full_reply.strip()})

        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    except Exception as e:
        print(f"Error in /chat: {e}")
        return StreamingResponse(
            iter(["Sorry, something went wrong. Please try again 😔"]),
            media_type="text/plain"
        )


print("Server ready! Open: http://127.0.0.1:8000/")
print(f"Conversation will be saved to: {LOG_FILE}")