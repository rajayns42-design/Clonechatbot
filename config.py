import os
from dotenv import load_dotenv

# Local testing ke liye .env file load karega
load_dotenv()

# --- 1. BOT IDENTITY ---
# Heroku variables se uthayega, agar nahi mile toh default blank
TOKEN = os.environ.get("TOKEN") or os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "@YourUsername")

# --- 2. TELEGRAM API (my.telegram.org se) ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH")

# --- 3. DATABASE (MongoDB Atlas URL) ---
MONGO_URL = os.environ.get("MONGO_URL", "")

# --- 4. AI ENGINE KEYS ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- 5. VISUALS & LINKS ---
START_IMG = os.environ.get("START_IMG", "https://graph.org/file/your-default-image.jpg")
SUPPORT_CHAT = os.environ.get("SUPPORT_GROUP", "https://t.me/YourGroup")
SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", "https://t.me/YourChannel")

# --- 6. LOGGING CHANNELS (Zaroori!) ---
# General errors ke liye
LOGGER_GROUP = int(os.environ.get("LOGGER_GROUP", "0"))
# Naye clone bots ki notification ke liye
CLONE_LOGGER = int(os.environ.get("CLONE_LOGGER", "0"))

# --- 7. LIMITS ---
MAX_CLONES = int(os.environ.get("MAX_CLONES", "9999"))
