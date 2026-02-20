from pymongo import MongoClient
import certifi
# Humne yahan 'Config' class ko import kiya hai
from .config import Config

# =========================
# MONGO CONNECT (SSL/TLS SAFE)
# =========================
# Ab hum Config.MONGO_URL use karenge
client = MongoClient(
    Config.MONGO_URL,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

db = client.natkhat_bot

# =========================
# COLLECTIONS
# =========================
users_collection = db["users"]              # For Broadcast
chats_collection = db["chats"]              # Chatbot status (ON/OFF)
sudo_collection = db["sudo_users"]          # Sudo/Admin list
welcome_collection = db["welcome_settings"] # Welcome status

# =========================
# USER STORE (BROADCAST)
# =========================
def register_user(user_id: int, first_name: str = None, username: str = None):
    """User ko database mein save ya update karta hai"""
    if not user_id: return
    users_collection.update_one(
        {"user_id": int(user_id)},
        {
            "$set": {
                "user_id": int(user_id),
                "name": first_name,
                "username": username
            }
        },
        upsert=True
    )

def get_all_users():
    """Saare broadcast users ki list nikalta hai"""
    data = users_collection.find({}, {"user_id": 1})
    return [int(x["user_id"]) for x in data if "user_id" in x]

def remove_user(user_id: int):
    users_collection.delete_one({"user_id": int(user_id)})

# =========================
# CHATBOT STATUS (ON/OFF)
# =========================
def set_chat_status(chat_id: int, status: bool):
    chats_collection.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"bot_on": bool(status)}},
        upsert=True
    )

def get_chat_status(chat_id: int) -> bool:
    chat = chats_collection.find_one({"chat_id": int(chat_id)})
    # Default Group mein Chatbot ON rahega
    return chat.get("bot_on", True) if chat else True

# =========================
# WELCOME STATUS
# =========================
def set_welcome_status(chat_id: int, status: bool):
    welcome_collection.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"welcome_on": bool(status)}},
        upsert=True
    )

def get_welcome_status(chat_id: int) -> bool:
    data = welcome_collection.find_one({"chat_id": int(chat_id)})
    return data.get("welcome_on", False) if data else False

# =========================
# SUDO USERS
# =========================
def add_sudo(user_id: int):
    sudo_collection.update_one(
        {"user_id": int(user_id)},
        {"$set": {"user_id": int(user_id)}},
        upsert=True
    )

def is_sudo(user_id: int) -> bool:
    return sudo_collection.find_one({"user_id": int(user_id)}) is not None

# =========================
# INITIAL OLD DATA SYNC
# =========================
def sync_old_users(user_list: list):
    """Purane users ko ek baar sync karne ke liye"""
    for uid in user_list:
        register_user(uid)
