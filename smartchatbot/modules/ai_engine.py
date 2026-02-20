import asyncio
import google.generativeai as genai
from groq import Groq
from mistralai.client import MistralClient
import httpx

from smartchatbot.config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    MISTRAL_API_KEY
)

# SYSTEM PROMPT: Natkhat personality aur short reply ke liye
SYSTEM_PROMPT = (
    "Tera naam NATKHAT hai. Tu ek chulbuli ladki hai. "
    "Rule: Reply ONLY in 2-3 Hinglish words + 1 emoji. "
    "Very short. No quotes. No long sentences."
)

# =========================
# HELPER: CLEAN TEXT
# =========================
def clean_reply(text: str) -> str:
    if not text: return ""
    return text.replace('"', '').replace("'", "").strip()

# =========================
# API WRAPPERS (With Auto-Switch Logic)
# =========================

async def ask_gemini(prompt: str):
    if not GEMINI_API_KEY: return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        loop = asyncio.get_event_loop()
        full_prompt = f"{SYSTEM_PROMPT}\nUser: {prompt}"
        response = await loop.run_in_executor(None, lambda: model.generate_content(full_prompt))
        return clean_reply(response.text)
    except: return None

async def ask_groq(prompt: str):
    if not GROQ_API_KEY: return None
    try:
        client = Groq(api_key=GROQ_API_KEY)
        loop = asyncio.get_event_loop()
        completion = await loop.run_in_executor(None, lambda: client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            max_tokens=15
        ))
        return clean_reply(completion.choices[0].message.content)
    except: return None

async def ask_mistral(prompt: str):
    if not MISTRAL_API_KEY: return None
    try:
        m_client = MistralClient(api_key=MISTRAL_API_KEY)
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, lambda: m_client.chat(
            model="mistral-small-latest",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
        ))
        return clean_reply(res.choices[0].message.content)
    except: return None

async def fallback_ai(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                "https://api.pawan.krd/v1/chat/completions",
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                }
            )
            data = r.json()
            return clean_reply(data["choices"][0]["message"]["content"])
    except:
        return "Theek hai na ✨" # Total failure par ek chota default reply

# =========================
# MASTER ENGINE (Immortal Switch)
# =========================

async def get_combined_ai_response(prompt: str) -> str:
    # Sequence: Gemini -> Groq -> Mistral -> Fallback
    
    # 1. Gemini
    response = await ask_gemini(prompt)
    if response: return response

    # 2. Groq (If Gemini fails)
    response = await ask_groq(prompt)
    if response: return response

    # 3. Mistral (If Groq fails)
    response = await ask_mistral(prompt)
    if response: return response

    # 4. Final Fallback (If all fail)
    return await fallback_ai(prompt)
