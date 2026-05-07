#!/usr/bin/env python3
"""
PuterAI Gateway — OpenAI-compatible API powered by Puter.js (no API keys needed)
Architecture: Python API ←→ bridge.html (browser) ←→ puter.ai.chat()
"""
import uuid, asyncio, time, json, os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any

# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(title="PuterAI Gateway", version="1.0.0",
              description="OpenAI-compatible API via Puter.js — no API keys needed")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory state ──────────────────────────────────────────────────────────
pending_queue:  dict[str, dict]         = {}   # id → request payload
result_store:   dict[str, Any]          = {}   # id → AI result
result_events:  dict[str, asyncio.Event] = {}  # id → asyncio signal
bridge_alive:   dict[str, float]        = {}   # track last bridge heartbeat

# ── Models ───────────────────────────────────────────────────────────────────
MODEL_MAP = {
    # Aliases → puter.js model strings
    "claude-opus-4-7":       "claude-opus-4-7",
    "claude-opus":           "claude-opus-4-7",
    "claude-opus-4-6":       "claude-opus-4-6",
    "claude-sonnet-4-6":     "claude-sonnet-4-6",
    "claude-sonnet":         "claude-sonnet-4-6",
    "claude-haiku-4-5":      "claude-haiku-4-5",
    "claude-haiku":          "claude-haiku-4-5",
    "gpt-4o":                "gpt-4o",
    "gpt-4":                 "gpt-4o",
    "gpt-4o-mini":           "gpt-4o-mini",
     
    "gpt-5.5-pro":           "gpt-5.5-pro",
    "gemini-3.1-pro":        "gemini-3.1-pro-preview",
    "gemini-3.1-flash":      "gemini-3.1-flash-lite-preview",
    "deepseek-v4":           "deepseek-v4-pro",



}

AVAILABLE_MODELS = [
    {"id": "claude-opus-4-7",   "object": "model", "created": 1713916800, "owned_by": "anthropic",
     "description": "Most capable Claude — adaptive thinking, 1M context"},
    {"id": "claude-sonnet-4-6", "object": "model", "created": 1706745600, "owned_by": "anthropic",
     "description": "Fast & powerful — near-flagship at lower cost"},
    {"id": "claude-haiku-4-5",  "object": "model", "created": 1696118400, "owned_by": "anthropic",
     "description": "Fastest Claude — ultra-low latency"},
    {"id": "gpt-4o",            "object": "model", "created": 1713916800, "owned_by": "openai",
     "description": "OpenAI GPT-4o via Puter.js"},
    {"id": "gpt-4o-mini",       "object": "model", "created": 1713916800, "owned_by": "openai",
     "description": "Lightweight GPT-4o via Puter.js"},

    {"id": "gpt-5.5-pro",       "object": "model", "created": 1713916800, "owned_by": "openai"},
    {"id": "gemini-3.1-pro",    "object": "model", "created": 1713916800, "owned_by": "google"},
    {"id": "gemini-3.1-flash",  "object": "model", "created": 1713916800, "owned_by": "google"},
    {"id": "deepseek-v4",       "object": "model", "created": 1713916800, "owned_by": "deepseek"},
]

# ── Pydantic schemas ──────────────────────────────────────────────────────────
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "claude-opus-4-7"
    messages: List[Message]
    stream: Optional[bool] = False
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7
    system: Optional[str] = None

# ── Helper ────────────────────────────────────────────────────────────────────
def bridge_is_connected() -> bool:
    if not bridge_alive:
        return False
    last = max(bridge_alive.values())
    return (time.time() - last) < 5.0   # 5-second timeout

# ── OpenAI-compatible API endpoints ──────────────────────────────────────────

@app.get("/v1/models")
@app.get("/models")
async def list_models():
    return {"object": "list", "data": AVAILABLE_MODELS}

@app.post("/v1/chat/completions")
@app.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    if not bridge_is_connected():
        raise HTTPException(
            status_code=503,
            detail=(
                "Bridge not connected. Open bridge.html in your browser first! "
                "Run: open http://localhost:8000/bridge"
            )
        )

    request_id   = str(uuid.uuid4())
    puter_model  = MODEL_MAP.get(request.model, request.model)
    messages     = [{"role": m.role, "content": m.content} for m in request.messages]

    # Prepend system message if provided
    if request.system:
        messages.insert(0, {"role": "system", "content": request.system})

    payload = {
        "id":        request_id,
        "model":     puter_model,
        "messages":  messages,
        "timestamp": time.time(),
    }

    # Enqueue and register event
    event = asyncio.Event()
    pending_queue[request_id]  = payload
    result_events[request_id]  = event

    try:
        await asyncio.wait_for(event.wait(), timeout=90.0)
    except asyncio.TimeoutError:
        pending_queue.pop(request_id, None)
        result_events.pop(request_id, None)
        raise HTTPException(
            status_code=504,
            detail="Request timed out. Is bridge.html still open and Puter logged in?"
        )

    result = result_store.pop(request_id, None)
    result_events.pop(request_id, None)

    if not result:
        raise HTTPException(status_code=500, detail="No result received from bridge")
    if "error" in result:
        raise HTTPException(status_code=502, detail=f"Puter.js error: {result['error']}")

    content = result.get("content", "")
        # ---- Build response ----
    prompt_chars = sum(len(m["content"]) for m in messages)
    completion_chars = len(content)
    return {
        "id":      f"chatcmpl-{request_id}",
        "object":  "chat.completion",
        "created": int(time.time()),
        "model":   request.model,
        "choices": [{
            "index":         0,
            "message":       {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens":     prompt_chars // 4,
            "completion_tokens": completion_chars // 4,
            "total_tokens":      (prompt_chars + completion_chars) // 4,
        },
    }

# ── Bridge endpoints (polled by bridge.html) ──────────────────────────────────

@app.get("/api/pending")
async def get_pending():
    """Bridge polls this every second to pick up new requests."""
    bridge_alive["last"] = time.time()

    # Clean up stale requests (>120s)
    stale = [k for k, v in pending_queue.items()
             if time.time() - v["timestamp"] > 120]
    for k in stale:
        pending_queue.pop(k, None)
        result_events.pop(k, None)

    if not pending_queue:
        return {"request": None}

    oldest = min(pending_queue.values(), key=lambda x: x["timestamp"])
    return {"request": oldest}

@app.post("/api/result")
async def post_result(data: dict):
    """Bridge posts the AI-generated result here."""
    request_id = data.get("id")
    if not request_id:
        return {"status": "error", "message": "Missing id"}

    pending_queue.pop(request_id, None)
    result_store[request_id] = data

    if request_id in result_events:
        result_events[request_id].set()

    return {"status": "ok"}

@app.get("/api/status")
async def api_status():
    return {
        "server":          "running",
        "bridge_connected": bridge_is_connected(),
        "pending_requests": len(pending_queue),
        "api_base":        "http://localhost:8000/v1",
        "bridge_url":      "http://localhost:8000/bridge",
    }

# ── Serve static files ────────────────────────────────────────────────────────

@app.get("/bridge")
async def serve_bridge():
    return FileResponse(os.path.join(os.path.dirname(__file__), "bridge.html"))

@app.get("/chat")
async def serve_chat():
    return FileResponse(os.path.join(os.path.dirname(__file__), "chatbot.html"))

@app.get("/")
async def root():
    return HTMLResponse("""
<!DOCTYPE html><html><body style="font-family:monospace;padding:2em;background:#0d1117;color:#58a6ff">
<h2>🚀 PuterAI Gateway</h2>
<p>Status: <span style="color:#3fb950">RUNNING</span></p>
<ul>
  <li><a href="/bridge" style="color:#58a6ff">🔗 Open Bridge (open this first!)</a></li>
  <li><a href="/chat"   style="color:#58a6ff">💬 Open Chatbot UI</a></li>
  <li><a href="/docs"   style="color:#58a6ff">📖 API Docs (Swagger)</a></li>
  <li><a href="/api/status" style="color:#58a6ff">📊 Status JSON</a></li>
</ul>
<p style="color:#8b949e">API base URL for Python: <code style="color:#e6edf3">http://localhost:8000/v1</code></p>
</body></html>
""")

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\n" + "═"*55)
    print("  🚀  PuterAI Gateway")
    print("═"*55)
    print("  API base:  http://localhost:8000/v1")
    print("  Bridge:    http://localhost:8000/bridge  ← open first!")
    print("  Chatbot:   http://localhost:8000/chat")
    print("  API docs:  http://localhost:8000/docs")
    print("═"*55 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
