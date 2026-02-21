import asyncio
import random
import google.generativeai as genai
from groq import Groq
from mistralai.client import MistralClient
import httpx

from smartchatbot.config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    MISTRAL_API_KEY
)

# --- Global Memory (Memory leak se bachne ke liye limit rakhi hai) ---
chat_memory = {}
sent_messages_log = {} # Har chat ke unique replies track karne ke liye

SYSTEM_PROMPT = (
    "Tera naam NATKHAT hai. Tu ek chulbuli aur shararati ladki hai. "
    "Rules: \n"
    "1. Reply ONLY in 2-3 Hinglish words + 1 emoji. \n"
    "2. Strict Rule: Never repeat your previous replies. Be unique. \n"
    "3. Human-like flirty and naughty nature. No robotic talk. \n"
    "4. No quotes, no formal language."
)

def clean_reply(text: str) -> str:
    if not text: return ""
    return text.replace('"', '').replace("'", "").strip()

# =========================
# API WRAPPERS (Priority Sequence)
# =========================

async def call_mistral(prompt: str):
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

async def call_groq(prompt: str):
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

async def call_gemini(prompt: str):
    if not GEMINI_API_KEY: return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: model.generate_content(f"{SYSTEM_PROMPT}\nUser: {prompt}"))
        return clean_reply(response.text)
    except: return None

async def call_free_api(prompt: str):
    # Yeh free GPT-3.5 API hai (Pawan.krd ya similar providers)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                "https://api.pawan.krd/v1/chat/completions",
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
                }
            )
            return clean_reply(r.json()["choices"][0]["message"]["content"])
    except: return None

# =========================
# MASTER ENGINE (Immortal Logic)
# =========================

async def get_combined_ai_response(chat_id, user_input: str) -> str:
    if chat_id not in sent_messages_log:
        sent_messages_log[chat_id] = set()
    
    # Priority order functions
    api_stack = [call_mistral, call_groq, call_gemini, call_free_api]
    
    final_reply = None
    
    # AI ko context dena taaki repeat na ho
    context_prompt = f"Previous replies: {list(sent_messages_log[chat_id])[-5:]}. Now answer: {user_input}"

    for api_call in api_stack:
        response = await api_call(context_prompt)
        
        # Check if response is unique and not empty
        if response and response not in sent_messages_log[chat_id]:
            final_reply = response
            sent_messages_log[chat_id].add(response)
            break # Sahi reply milte hi loop band
            
    # Agar saari APIs ne repeat kiya (very rare), toh force unique reply
    if not final_reply:
        final_reply = f"Kuch naya pucho {random.choice(['😜', '💖', '✨'])}"

    # Memory Cleanup (History ko 20 messages tak limited rakho taaki slow na ho)
    if len(sent_messages_log[chat_id]) > 20:
        sent_messages_log[chat_id].pop() 

    return final_reply
