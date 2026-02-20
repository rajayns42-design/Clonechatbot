import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # =========================
    # BOT IDENTITY
    # =========================
    BOT_TOKEN = os.environ.get("TOKEN") or os.environ.get("BOT_TOKEN")
    OWNER_ID = int(os.environ.get("OWNER_ID", "8321028072"))
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "@ll_WTF_HARI_ll")

    # =========================
    # TELEGRAM API
    # =========================
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH")

    # =========================
    # DATABASE
    # =========================
    MONGO_URL = os.environ.get(
        "MONGO_URL",
        "mongodb+srv://Ange:Angel143@cluster0.eg8qb2a.mongodb.net/?appName=Cluster0"
    )

    # =========================
    # AI KEYS
    # =========================
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

    # =========================
    # VISUALS & LINKS
    # =========================
    START_IMG = os.environ.get("START_IMG", "https://graph.org/file/your-default-image.jpg")
    SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "https://t.me/Love_Ki_Duniyaa")
    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/Love_Bot_143")

    # =========================
    # LOGGING
    # =========================
    LOGGER_GROUP = int(os.environ.get("LOGGER_GROUP", "-1003605595874"))

# ==========================================
# IMPORTANT: DO NOT REMOVE THIS PART
# Ye lines aapke 'ImportError' ko fix karengi
# ==========================================
BOT_TOKEN = Config.BOT_TOKEN
OWNER_ID = Config.OWNER_ID
OWNER_USERNAME = Config.OWNER_USERNAME
API_ID = Config.API_ID
API_HASH = Config.API_HASH
MONGO_URL = Config.MONGO_URL
GEMINI_API_KEY = Config.GEMINI_API_KEY
MISTRAL_API_KEY = Config.MISTRAL_API_KEY
GROQ_API_KEY = Config.GROQ_API_KEY
START_IMG = Config.START_IMG
SUPPORT_GROUP = Config.SUPPORT_GROUP
UPDATE_CHANNEL = Config.UPDATE_CHANNEL
LOGGER_GROUP = Config.LOGGER_GROUP
# ==========================================
