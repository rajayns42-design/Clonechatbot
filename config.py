import os

# Heroku Dashboard 'Config Vars' se data uthane ke liye
# Agar local pe chala rahe ho toh os.environ.get ki jagah dotenv use kar sakte ho

# --- BOT IDENTITY ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "@YourUsername")

# --- TELEGRAM API ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH")

# --- DATABASE (Heroku ke liye MongoDB zaroori hai) ---
# MongoDB Atlas se free URL lein
MONGO_URL = os.environ.get("MONGO_URL", "")

# --- AI ENGINE KEYS ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- VISUALS & LINKS ---
START_IMG = os.environ.get("START_IMG", "https://telegra.ph/file/default.jpg")
SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", "https://t.me/YourChannel")
SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "https://t.me/YourGroup")

# --- LOGGING CHANNELS ---
LOGGER_GROUP = int(os.environ.get("LOGGER_GROUP", "0"))
CLONE_LOGGER = int(os.environ.get("CLONE_LOGGER", "0"))

# --- SETTINGS ---
MAX_CLONES = 9999
