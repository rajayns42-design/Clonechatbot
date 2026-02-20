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
# BROADCAST USERS (OLD LIST ADD)
# =========================
broadcast_users = [
    123456789, 234567890, 345678901, 456789012, 567890123
    # ... yahan apne jitne bhi old broadcast user IDs hain daal do
]

for user_id in broadcast_users:
    add_user(user_id)

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
