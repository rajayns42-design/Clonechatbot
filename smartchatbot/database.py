from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client.natkhat_bot

# Collections
chats_collection = db["chats"]
clones_collection = db["cloned_bots"]
warns_collection = db["user_warns"] # Warns record karne ke liye

# --- 1. Chat & Welcome Status ---
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

# --- 2. AI Model Selection (Mistral/Groq/Gemini) ---
def set_bot_ai(bot_id, model_name):
    """Har clone bot apni pasand ka AI model save kar sakega"""
    clones_collection.update_one({"bot_id": bot_id}, {"$set": {"ai_model": model_name}}, upsert=True)

def get_bot_ai(bot_id):
    bot = clones_collection.find_one({"bot_id": bot_id})
    return bot.get("ai_model", "gemini") if bot else "gemini"

# --- 3. Warn System Logic ---
def add_warn(chat_id, user_id):
    """User ko warn karega aur count return karega"""
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

# --- 4. Clone Bot Persistence ---
def add_cloned_bot(user_id, token, username, bot_id):
    data = {
        "user_id": user_id,
        "token": token,
        "username": username,
        "bot_id": bot_id,
        "status": "active"
    }
    clones_collection.update_one({"token": token}, {"$set": data}, upsert=True)

def get_all_bots():
    return list(clones_collection.find({"status": "active"}))

def remove_cloned_bot(token):
    clones_collection.delete_one({"token": token})

