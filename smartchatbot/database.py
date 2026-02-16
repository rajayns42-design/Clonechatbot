from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client.natkhat_bot
clones_collection = db["cloned_bots"] # Naya collection clones ke liye

# --- Chat & Welcome Status Functions ---
def set_chat_status(chat_id, status: bool):
    db.chats.update_one({"chat_id": chat_id}, {"$set": {"bot_on": status}}, upsert=True)

def get_chat_status(chat_id):
    chat = db.chats.find_one({"chat_id": chat_id})
    return chat.get("bot_on", True) if chat else True

def set_welcome_status(chat_id, status: bool):
    db.chats.update_one({"chat_id": chat_id}, {"$set": {"welcome_on": status}}, upsert=True)

def get_welcome_status(chat_id):
    chat = db.chats.find_one({"chat_id": chat_id})
    return chat.get("welcome_on", True) if chat else True

# --- New: Clone Bot Persistence Functions ---
def add_cloned_bot(user_id, token, username):
    data = {
        "user_id": user_id,
        "token": token,
        "username": username,
        "status": "active"
    }
    clones_collection.update_one({"token": token}, {"$set": data}, upsert=True)

def get_all_bots():
    return list(clones_collection.find({"status": "active"}))

def remove_cloned_bot(token):
    clones_collection.delete_one({"token": token})
