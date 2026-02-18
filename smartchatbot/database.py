from pymongo import MongoClient
from .config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client.natkhat_bot

# =========================
# COLLECTIONS
# =========================
chats_collection = db["chats"]
clones_collection = db["cloned_bots"]
sudo_collection = db["sudo_users"]
welcome_collection = db["welcome_settings"]

# =========================
# AI SELECTION
# =========================
def get_bot_ai(bot_id):
    """Specific clone bot ke liye selected AI engine"""
    bot = clones_collection.find_one({"bot_id": bot_id})
    return bot.get("selected_ai", "gemini") if bot else "gemini"


# =========================
# CHAT STATUS
# =========================
def set_chat_status(chat_id, status: bool):
    chats_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"bot_on": status}},
        upsert=True
    )

def get_chat_status(chat_id):
    chat = chats_collection.find_one({"chat_id": chat_id})
    return chat.get("bot_on", True) if chat else True


# =========================
# WELCOME STATUS  ✅ FIX
# =========================
def set_welcome_status(chat_id, status: bool):
    welcome_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome_on": status}},
        upsert=True
    )

def get_welcome_status(chat_id):
    data = welcome_collection.find_one({"chat_id": chat_id})
    return data.get("welcome_on", False) if data else False


# =========================
# CLONE MANAGEMENT
# =========================
def add_cloned_bot(user_id, token, username, bot_id):
    data = {
        "user_id": user_id,
        "token": token,
        "username": username,
        "bot_id": bot_id,
        "status": "active",
        "selected_ai": "gemini"
    }

    clones_collection.update_one(
        {"token": token},
        {"$set": data},
        upsert=True
    )


def get_all_bots():
    return list(clones_collection.find({"status": "active"}))


def remove_cloned_bot(token):
    clones_collection.update_one(
        {"token": token},
        {"$set": {"status": "inactive"}}
    )


# =========================
# SUDO USERS (optional but safe)
# =========================
def add_sudo(user_id):
    sudo_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

def is_sudo(user_id):
    return sudo_collection.find_one({"user_id": user_id}) is not None
