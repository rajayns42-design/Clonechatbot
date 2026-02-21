import asyncio
import random
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral
import httpx

from telegram import Update
from telegram.ext import ContextTypes
from ..database import get_chat_status, set_chat_status
from ..config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OWNER_ID

# --- API Setup ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash") 
groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

# --- Memory & Anti-Repeat Tracker ---
chat_memory = {}
sent_replies_log = {}

SYSTEM_PROMPT = (
    "Tera naam NATKHAT hai. Tu ek chulbuli aur shararati ladki hai. "
    "Rules: \n"
    "1. Reply ONLY in 2 to 3 Hinglish words + 1 emoji. \n"
    "2. Strict Rule: Never repeat previous replies. Be unique. \n"
    "3. Human-like flirty/naughty girl nature. No robotic talk. \n"
    "4. No quotes, no formal language."
)

def clean_reply(text: str) -> str:
    if not text: return ""
    return text.replace('"', '').replace("'", "").strip()

# =========================
# IMMORTAL API STACK
# =========================

async def call_mistral(prompt: str):
    if not MISTRAL_API_KEY: return None
    try:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, lambda: mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
        ))
        return clean_reply(res.choices[0].message.content)
    except: return None

async def call_groq(prompt: str):
    if not GROQ_API_KEY: return None
    try:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, lambda: groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            max_tokens=20
        ))
        return clean_reply(res.choices[0].message.content)
    except: return None

async def call_gemini(prompt: str):
    if not GEMINI_API_KEY: return None
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: gemini_model.generate_content(f"{SYSTEM_PROMPT}\nUser: {prompt}"))
        return clean_reply(response.text)
    except: return None

async def call_free_api(prompt: str):
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
# MASTER ENGINE
# =========================

async def get_ai_reply(chat_id, text: str):
    if chat_id not in sent_replies_log:
        sent_replies_log[chat_id] = set()
    
    api_stack = [call_mistral, call_groq, call_gemini, call_free_api]
    history = "\n".join(chat_memory.get(chat_id, [])[-6:])
    full_prompt = f"History:\n{history}\nUser: {text}\nNATKHAT (Important: Don't repeat):"

    final_reply = None
    for api_call in api_stack:
        response = await api_call(full_prompt)
        if response and response not in sent_replies_log[chat_id]:
            final_reply = response
            sent_replies_log[chat_id].add(response)
            break

    if not final_reply:
        final_reply = random.choice(["Acha ji? 😜", "Pagal hai kya! 😂", "Hehe, batao ✨", "Hmm, socho 🤔"])

    if chat_id not in chat_memory: chat_memory[chat_id] = []
    chat_memory[chat_id].append(f"User: {text}")
    chat_memory[chat_id].append(f"NATKHAT: {final_reply}")
    
    if len(chat_memory[chat_id]) > 10: chat_memory[chat_id] = chat_memory[chat_id][-10:]
    if len(sent_replies_log[chat_id]) > 40: sent_replies_log[chat_id].clear()

    return final_reply

# =========================
# TOGGLE & REPLY HANDLERS
# =========================

async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        return await update.message.reply_text("<blockquote>Main hamesha on hu yahan! 😉</blockquote>", parse_mode="HTML")

    # Admin Check
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"] and user.id != OWNER_ID:
            return await update.message.reply_text("<blockquote>❌ Sirf Admins mujhe control kar sakte hain!</blockquote>", parse_mode="HTML")
    except: pass

    if not context.args:
        return await update.message.reply_text("<blockquote>Usage: /chatbot on | off</blockquote>", parse_mode="HTML")

    action = context.args[0].lower()
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text("<blockquote>✅ NATKHAT Active! Ab mazaa aayega. 😉</blockquote>", parse_mode="HTML")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text("<blockquote>📴 Main sone ja rahi hu. Bye! 🥺</blockquote>", parse_mode="HTML")

async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if update.message.text.startswith("/"): return

    chat = update.effective_chat
    
    # Check Status (Important)
    if chat.type != "private" and not get_chat_status(chat.id):
        return

    await context.bot.send_chat_action(chat_id=chat.id, action="typing")
    reply = await get_ai_reply(chat.id, update.message.text)
    if reply:
        await update.message.reply_text(reply)
