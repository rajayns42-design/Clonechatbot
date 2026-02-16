import google.generativeai as genai
from groq import Groq
from mistralai.client import MistralClient
import httpx # Iske liye 'pip install httpx' zaroori hai
from config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY

async def fallback_ai(prompt):
    """
    Jab saare API keys fail ho jayein, tab ye free public engine use hoga.
    """
    try:
        # Hum yahan ek free public AI API use kar rahe hain jo open hai
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.pawan.krd/v1/chat/completions", # Example Public API
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=10.0
            )
            res_data = response.json()
            return res_data['choices'][0]['message']['content']
    except Exception:
        return "❌ Saare AI engines (Gemini, Groq, Mistral, Free) down hain. Kripya 1 minute baad try karein."

async def get_combined_ai_response(prompt):
    # 1. TRY GEMINI
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            if response.text: return response.text
        except: pass

    # 2. TRY GROQ
    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        except: pass

    # 3. TRY MISTRAL
    if MISTRAL_API_KEY:
        try:
            m_client = MistralClient(api_key=MISTRAL_API_KEY)
            m_res = m_client.chat(model="mistral-small-latest", messages=[{"role": "user", "content": prompt}])
            return m_res.choices[0].message.content
        except: pass

    # 4. ULTIMATE BACKUP (Jab kuch kaam na kare)
    return await fallback_ai(prompt)
