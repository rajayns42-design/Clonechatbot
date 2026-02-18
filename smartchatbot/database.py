from pymongo import MongoClient
from .config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client.natkhat_bot

# Collections
chats_collection = db["chats"]
clones_collection = db["cloned_bots"]
sudo_collection = db["sudo_users"] 

# --- AI Selection Function (Iske bina bot crash ho raha tha) ---
def get_bot_ai(bot_id):
    """Specific clone bot ke liye selected AI engine dhoondne ke liye"""
    bot = clones_collection.find_one({"bot_id": bot_id})
    # Default model 'gemini' rakha gaya hai
    return bot.get("selected_ai", "gemini") if bot else "gemini"

# --- Chat & Welcome Status ---
def set_chat_status(chat_id, status: bool):
    chats_collection.update_one({"chat_id": chat_id}, {"$set": {"bot_on": status}}, upsert=True)

def get_chat_status(chat_id):
    chat = chats_collection.find_one({"chat_id": chat_id})
    return chat.get("bot_on", True) if chat else True

# --- Clone Management ---
def add_cloned_bot(user_id, token, username, bot_id):
    data = {
        "user_id": user_id,
        "token": token,
        "username": username,
        "bot_id": bot_id,
        "status": "active",
        "selected_ai": "gemini"
    }
    clones_collection.update_one({"token": token}, {"$set": data}, upsert=True)

def get_all_bots():
    return list(clones_collection.find({"status": "active"}))

def remove_cloned_bot(token):
    clones_collection.update_one({"token": token}, {"$set": {"status": "inactive"}})
