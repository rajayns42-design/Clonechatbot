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
    bot = clones_collection.find_one({"bot_id": bot_id})
    return bot.get("selected_ai", "gemini") if bot else "gemini"


def set_bot_ai(bot_id, model_name: str):
    clones_collection.update_one(
        {"bot_id": bot_id},
        {"$set": {"selected_ai": model_name}},
        upsert=True
    )

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
# WELCOME STATUS
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
        "user_id": user_id,     # ✅ clone owner
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


def remove_cloned_bot(token):
    clones_collection.update_one(
        {"token": token},
        {"$set": {"status": "inactive"}}
    )


def get_all_bots():
    """All active clones — restart restore ke kaam aayega"""
    return list(clones_collection.find({"status": "active"}))


# =========================
# ✅ NEW — OWNER LOOKUPS
# =========================

def get_clone_owner_by_token(token):
    bot = clones_collection.find_one({"token": token})
    return bot.get("user_id") if bot else None


def get_clone_owner_by_botid(bot_id):
    bot = clones_collection.find_one({"bot_id": bot_id})
    return bot.get("user_id") if bot else None


def is_clone_active(token):
    return clones_collection.find_one({
        "token": token,
        "status": "active"
    }) is not None


# =========================
# ✅ NEW — USER CLONE LIST
# =========================

def get_user_clones(user_id):
    return list(clones_collection.find({
        "user_id": user_id,
        "status": "active"
    }))


# =========================
# SUDO USERS
# =========================

def add_sudo(user_id):
    sudo_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

def remove_sudo(user_id):
    sudo_collection.delete_one({"user_id": user_id})

def is_sudo(user_id):
    return sudo_collection.find_one({"user_id": user_id}) is not None
