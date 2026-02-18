from pymongo import MongoClient
import certifi
from .config import MONGO_URL

# =========================
# MONGO CONNECT (HEROKU SAFE)
# =========================

client = MongoClient(
    MONGO_URL,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

db = client.natkhat_bot


# =========================
# COLLECTIONS
# =========================

users_collection = db["users"]              # broadcast users
chats_collection = db["chats"]              # Chatbot status (ON/OFF)
clones_collection = db["cloned_bots"]
sudo_collection = db["sudo_users"]
welcome_collection = db["welcome_settings"]


# =========================
# USER STORE (GLOBAL BROADCAST)
# =========================

def add_user(user_id: int):
    if not user_id:
        return
    users_collection.update_one(
        {"user_id": int(user_id)},
        {"$set": {"user_id": int(user_id)}},
        upsert=True
    )

def get_all_users():
    data = users_collection.find({}, {"user_id": 1})
    return [int(x["user_id"]) for x in data if "user_id" in x]

def remove_user(user_id: int):
    users_collection.delete_one({"user_id": int(user_id)})


# =========================
# CHATBOT STATUS (ON/OFF)
# =========================

def set_chat_status(chat_id, status: bool):
    """Chatbot ko enable ya disable karne ke liye status set karta hai"""
    chats_collection.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"bot_on": bool(status)}},
        upsert=True
    )

def get_chat_status(chat_id):
    """Check karta hai ki chatbot ON hai ya nahi. Default: True (ON)"""
    chat = chats_collection.find_one({"chat_id": int(chat_id)})
    if not chat:
        return True
    return chat.get("bot_on", True)


# =========================
# AI SELECTION
# =========================

def get_bot_ai(bot_id):
    bot = clones_collection.find_one({"bot_id": bot_id})
    if not bot:
        return "gemini"
    return bot.get("selected_ai", "gemini")

def set_bot_ai(bot_id, model_name: str):
    clones_collection.update_one(
        {"bot_id": bot_id},
        {"$set": {"selected_ai": model_name}},
        upsert=True
    )


# =========================
# WELCOME STATUS
# =========================

def set_welcome_status(chat_id, status: bool):
    welcome_collection.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"welcome_on": bool(status)}},
        upsert=True
    )

def get_welcome_status(chat_id):
    data = welcome_collection.find_one({"chat_id": int(chat_id)})
    return data.get("welcome_on", False) if data else False


# =========================
# CLONE MANAGEMENT
# =========================

def add_cloned_bot(user_id, token, username, bot_id):
    data = {
        "user_id": int(user_id),
        "token": token,
        "username": username,
        "bot_id": int(bot_id),
        "status": "active",
        "selected_ai": "gemini"
    }
    clones_collection.update_one(
        {"token": token},
        {"$set": data},
        upsert=True
    )

def remove_cloned_bot(token):
    clones_collection.update_one(
        {"token": token},
        {"$set": {"status": "inactive"}}
    )

def get_all_bots():
    """Sirf active clones ko wapas lata hai"""
    return list(clones_collection.find({"status": "active"}))

def is_clone_active(token):
    return clones_collection.find_one({
        "token": token,
        "status": "active"
    }) is not None


# =========================
# SUDO & OWNER LOOKUPS
# =========================

def add_sudo(user_id):
    sudo_collection.update_one(
        {"user_id": int(user_id)},
        {"$set": {"user_id": int(user_id)}},
        upsert=True
    )

def remove_sudo(user_id):
    sudo_collection.delete_one({"user_id": int(user_id)})

def is_sudo(user_id):
    return sudo_collection.find_one({"user_id": int(user_id)}) is not None

def get_clone_owner_by_token(token):
    bot = clones_collection.find_one({"token": token})
    return int(bot["user_id"]) if bot else None

def get_clone_owner_by_botid(bot_id):
    bot = clones_collection.find_one({"bot_id": int(bot_id)})
    return int(bot["user_id"]) if bot else None

def get_user_clones(user_id):
    return list(clones_collection.find({
        "user_id": int(user_id),
        "status": "active"
    }))
