import os
from dotenv import load_dotenv

# Local testing ke liye .env file load karega
load_dotenv()

# --- 1. BOT IDENTITY ---
# Heroku variables se uthayega, agar nahi mile toh default blank
TOKEN = os.environ.get("TOKEN") or os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "8321028072"))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "@ll_WTF_HARI_ll")

# --- 2. TELEGRAM API (my.telegram.org se) ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH")

# --- 3. DATABASE (MongoDB Atlas URL) ---
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://Ange:Angel143@cluster0.eg8qb2a.mongodb.net/?appName=Cluster0")

# --- 4. AI ENGINE KEYS ---
GEMINI_API_KEY = os.environ.get("AIzaSyDVTjxpAdFwUKaHOgVb8ofOQ7g3j8CdXDM")
MISTRAL_API_KEY = os.environ.get("gV6LlP2Zq2AoWdP5SizLcmdRDBboCR3q")
GROQ_API_KEY = os.environ.get("")

# --- 5. VISUALS & LINKS ---
START_IMG = os.environ.get("START_IMG", "https://graph.org/file/your-default-image.jpg")
SUPPORT_CHAT = os.environ.get("SUPPORT_GROUP", "https://t.me/Love_Ki_Duniyaa")
SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", "https://t.me/Love_Bot_143")

# --- 6. LOGGING CHANNELS (Zaroori!) ---
# General errors ke liye
LOGGER_GROUP = int(os.environ.get("LOGGER_GROUP", "-1003605595874"))
# Naye clone bots ki notification ke liye
CLONE_LOGGER = int(os.environ.get("CLONE_LOGGER", "-1003605595874"))

# --- 7. LIMITS ---
MAX_CLONES = int(os.environ.get("MAX_CLONES", "9999"))
