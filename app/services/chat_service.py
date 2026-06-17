
import httpx
import json
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

async def ask_gemini(req):
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY")
    if not GEMINI_MODEL:
        raise ValueError("Missing GEMINI_MODEL")

    try:
        system_text = (
            "You are RetinaScan AI, a specialized ophthalmology imaging assistant. "
            "Help clinicians understand retinal scan results. "
            "Always clarify this is for clinical guidance only — not a definitive diagnosis."
        )

        if req.scan_context:
            system_text += "\n\nSCAN:\n" + json.dumps(
                req.scan_context,
                indent=2
            )

        contents = []

        # Previous chat history
        for m in req.history:
            contents.append({
                "role": "model" if m.role == "assistant" else "user",
                "parts": [{"text": m.content}]
            })

        # Current user message
        contents.append({
            "role": "user",
            "parts": [{"text": req.message}]
        })

        url = (
            "https://generativelanguage.googleapis.com/"
            f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        )

        payload = {
            "systemInstruction": {
                "parts": [{"text": system_text}]
            },
            "contents": contents
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)

        if resp.status_code != 200:
            raise RuntimeError(
                f"Gemini API Error {resp.status_code}: {resp.text}"
            )

        data = resp.json()

        return (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

    except httpx.RequestError as e:
        raise RuntimeError(f"Network error: {e}")
    except Exception as e:
        raise RuntimeError(f"Chat error: {e}")