from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client.natkhat_bot

# Collections
chats_collection = db["chats"]
clones_collection = db["cloned_bots"]
warns_collection = db["user_warns"]
sudo_collection = db["sudo_users"] 

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

# --- 2. Broadcast Helper (Groups List) ---
def get_all_chats():
    """Broadcast ke liye saari unique group IDs nikalne ke liye"""
    return chats_collection.find({}, {"chat_id": 1})

# --- 3. Sudo User Management ---
def add_sudo(user_id):
    sudo_collection.update_one({"user_id": user_id}, {"$set": {"is_sudo": True}}, upsert=True)

def is_sudo(user_id):
    user = sudo_collection.find_one({"user_id": user_id})
    return bool(user)

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
    # Data delete nahi hoga, bas status inactive ho jayega (Safe side)
    clones_collection.update_one({"token": token}, {"$set": {"status": "inactive"}})
