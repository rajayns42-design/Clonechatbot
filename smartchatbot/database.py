import pymongo
import os
from config import MONGO_URL

# Connection setup
client = pymongo.MongoClient(MONGO_URL)
db = client["smartbot_db"]
clones = db["cloned_bots"]

def add_cloned_bot(user_id, token, username):
    data = {
        "user_id": user_id,
        "token": token,
        "username": username,
        "status": "active"
    }
    # Agar token pehle se hai toh update karein, nahi toh insert
    clones.update_one({"token": token}, {"$set": data}, upsert=True)
    print(f"✅ Bot saved in Cloud: {username}")

def get_all_bots():
    all_bots = clones.find({"status": "active"})
    return [bot["token"] for bot in all_bots]

