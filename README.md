# PuterAI Gateway

> **Free, unlimited access to GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro/Flash, and DeepSeek V4 — no API keys needed.**

A zero‑configuration API gateway that uses [Puter.js](https://js.puter.com/v2/) to provide OpenAI‑compatible endpoints for five frontier AI models, completely free.

## Architecture
```

User/App → Python FastAPI (OpenAI‑compatible) → stores request in queue
│
bridge.html (open in browser) polls every 1s
│
picks up request → calls puter.ai.chat()
│
sends result back → Python returns JSON → User gets response```
```

**No Playwright, no headless browsers, no API keys.**

The bridge runs in a real browser tab — you log into Puter once and keep it open.

## Features

- **OpenAI‑compatible API** — Works with any OpenAI SDK client by changing `base_url`
    
- **Free AI Access** — Uses Puter.js browser‑based AI (free Puter account required)
    
- **Five Models**: GPT‑5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Gemini 3.1 Flash, DeepSeek V4
    
- **Streaming support** — SSE‑based streaming responses
    
- **File upload** — Via chat UI (`/chat`), files are injected into the prompt
    
- **Chat UI included** — A sleek, ChatGPT‑style interface at `/chat`

## Requirements

- Python 3.10+
    
- A free [Puter.com](https://puter.com/) account
    
- Internet connection

## Quick Start

### 1. Run the server

```bash
chmod +x run.sh
./run.sh
```
### 2. Open the bridge

- Go to `http://localhost:8000/bridge` in your browser.
    
- Log into Puter when prompted (free account).
    
- Keep this tab open — it handles all API requests.


### 3. Use the API

Bash

```
# Basic chat
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-opus-4.7","messages":[{"role":"user","content":"Hello"}]}'
```

_Or open `http://localhost:8000/docs` for the Swagger UI._

---

## API Usage

### Python SDK

```Python


from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="no-key-needed"
)

response = client.chat.completions.create(
    model="claude-opus-4.7",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)


### Streaming

Python


stream = client.chat.completions.create(
    model="gpt-5.5-pro",
    messages=[{"role": "user", "content": "Write a haiku"}],
    stream=True
)

for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
```


---

## API Endpoints

|**Method**|**Path**|**Description**|
|---|---|---|
|GET|`/health`|Server health status|
|GET|`/v1/models`|List available models|
|POST|`/v1/chat/completions`|Chat completion (OpenAI‑compatible)|
|GET|`/api/status`|Bridge/server connection status|
|GET|`/bridge`|Open the bridge page|
|GET|`/chat`|Open the chatbot UI|
|GET|`/docs`|Swagger API documentation|

## Supported Models

| **API Model**      | **Puter.js Model ID**                  | **Provider** |
| ------------------ | -------------------------------------- | ------------ |
| `gpt-5.5-pro`      | `openai/gpt-5.5-pro`                   | OpenAI       |
| `claude-opus-4.7`  | `anthropic/claude-opus-4-7`            | Anthropic    |
| `gemini-3.1-pro`   | `google/gemini-3.1-pro-preview`        | Google       |
| `gemini-3.1-flash` | `google/gemini-3.1-flash-lite-preview` | Google       |
| `deepseek-v4`      | `deepseek/deepseek-v4-pro`             | DeepSeek     |

---

## Project Structure

```


├── server.py        # FastAPI server (OpenAI‑compatible endpoints)
├── bridge.html      # Bridge page (open in browser — handles AI calls)
├── chatbot.html     # Chat UI (optional — direct Puter.js chat interface)
├── requirements.txt # Dependency
├── test_api.py # API testing
└── README.md   # This file
```



---

## Troubleshooting

| **Symptom**                          | **Fix**                                                     |
| ------------------------------------ | ----------------------------------------------------------- |
| "No user message found"              | Send valid JSON with `"role": "user"` and `"content"`       |
| Bridge stuck on "Checking Puter.js…" | Click Login to Puter button                                 |
| Server offline in bridge             | Run `python server.py` from the project directory           |
| Bridge page shows no models          | Ensure `bridge.html` and `server.py` are in the same folder |

---

## How It Works Under the Hood

1. Your app sends a request to `/v1/chat/completions`
    
2. Python stores it in an in‑memory queue with a unique ID
    
3. `bridge.html` (open in your browser) polls `/api/pending` every second
    
4. When it sees a pending request, it calls `puter.ai.chat()` with the mapped model
    
5. The AI response is sent back to Python via `/api/result`
    
6. Python returns the result in OpenAI‑compatible JSON format
    

All AI calls go through your authenticated browser session — no server‑side API keys are ever needed.

---

## ⚠️ Disclaimer

This project relies on the free tier of **Puter.js**, which advertises itself as *“free unlimited AI.”*  
In practice, Puter’s free tier has **undocumented per-account daily limits** (commonly ~100 requests) and may return errors like `usage-limited-chat` or `insufficient_funds`.  
**Models sometimes self‑identify as older versions** even when the underlying model is the latest (a known issue with certain AI providers).

### What this means for you

- The gateway works, but **usage is not infinitely free** – hidden limits apply.
- The multi‑account rotation feature helps **extend** your free usage, but it cannot eliminate limits entirely.
- If you need **reliable, unlimited access to frontier models** (GPT‑5.5 Pro, Claude Opus 4.7, Gemini 3.1), consider:
  - Running models locally with [Ollama](https://ollama.com) or [Jan AI](https://jan.ai) (fully free, offline).
  - Using the transparent freemium tiers of services like [Pollinations.AI](https://pollinations.ai) or [OpenRouter](https://openrouter.ai).
  - Using official pay‑as‑you‑go APIs from OpenAI, Anthropic, Google, or DeepSeek.

The creators of this project are **not affiliated with Puter.js** and provide this gateway as a community tool – use it at your own risk. No guarantees of uptime, model quality, or availability are made.

---

## License

MIT License

---
## Contributing

Issues and pull requests welcome!
---

## Test on Github Pages

 ---

















<!-- LIVE_URL_START -->
🌐 **Live Server URL:** https://assembled-viewers-aurora-insider.trycloudflare.com  
🔗 **Bridge:** https://assembled-viewers-aurora-insider.trycloudflare.com/bridge  
💬 **Chat UI:** https://assembled-viewers-aurora-insider.trycloudflare.com/chat  
📄 **API Docs:** https://assembled-viewers-aurora-insider.trycloudflare.com/docs  
🌐 **API Endpoint:** https://assembled-viewers-aurora-insider.trycloudflare.com/v1  
⏱️ *Updated: 2026-06-18 06:27:58 UTC*  
<!-- LIVE_URL_END -->
