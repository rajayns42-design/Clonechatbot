from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client.natkhat_bot

# Collections
chats_collection = db["chats"]
clones_collection = db["cloned_bots"]
warns_collection = db["user_warns"]
sudo_collection = db["sudo_users"] # Restart ke baad Sudo powers na uden

# --- 1. Chat & Welcome Status (Data Safe) ---
def set_chat_status(chat_id, status: bool):
    chats_collection.update_one({"chat_id": chat_id}, {"$set": {"bot_on": status}}, upsert=True)

def get_chat_status(chat_id):
    chat = chats_collection.find_one({"chat_id": chat_id})
    return chat.get("bot_on", True) if chat else True

def set_welcome_status(chat_id, status: bool):
    chats_collection.update_one({"chat_id": chat_id}, {"$set": {"welcome_on": status}}, upsert=True)

def get_welcome_status(chat_id):
    chat = chats_collection.find_one({"chat_id": chat_id})
    return chat.get("welcome_on", True) if chat else True

# --- 2. AI Model Selection ---
def set_bot_ai(bot_id, model_name):
    clones_collection.update_one({"bot_id": bot_id}, {"$set": {"ai_model": model_name}}, upsert=True)

def get_bot_ai(bot_id):
    bot = clones_collection.find_one({"bot_id": bot_id})
    return bot.get("ai_model", "gemini") if bot else "gemini"

# --- 3. Warn System (Persistent) ---
def add_warn(chat_id, user_id):
    warn_data = warns_collection.find_one({"chat_id": chat_id, "user_id": user_id})
    new_count = (warn_data.get("count", 0) + 1) if warn_data else 1
    warns_collection.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": new_count}},
        upsert=True
    )
    return new_count

def reset_warns(chat_id, user_id):
    warns_collection.delete_one({"chat_id": chat_id, "user_id": user_id})

# --- 4. NEW: Boot Persistence (For Restart Safety) ---
def save_bot_session(bot_id, session_data):
    """Restart ke baad bot ka session yaha se load hoga"""
    clones_collection.update_one({"bot_id": bot_id}, {"$set": {"session": session_data}}, upsert=True)

def add_cloned_bot(user_id, token, username, bot_id):
    data = {
        "user_id": user_id,
        "token": token,
        "username": username,
        "bot_id": bot_id,
        "status": "active"
    }
    # Upsert=True se data overwrite nahi hota balki update hota hai
    clones_collection.update_one({"token": token}, {"$set": data}, upsert=True)

def get_all_bots():
    """Ye main function hai jo restart pe saare tokens nikalega"""
    return list(clones_collection.find({"status": "active"}))

def remove_cloned_bot(token):
    clones_collection.update_one({"token": token}, {"$set": {"status": "inactive"}})
