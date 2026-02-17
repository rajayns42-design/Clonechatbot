# ⚡ NATKHAT AI — The Ultimate Bot Cloner System

<p align="center">
  <img src="https://graph.org/file/your-image-id.jpg" alt="Natkhat AI Logo" width="200">
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/yourusername/natkhat-ai?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/github/forks/yourusername/natkhat-ai?style=for-the-badge" alt="Forks">
  <img src="https://img.shields.io/github/license/yourusername/natkhat-ai?style=for-the-badge" alt="License">
</p>

**Natkhat AI** ek high-performance Telegram bot hai jo users ko apna khud ka bot clone karne ki suvidha deta hai. Yeh **Gemini, Groq, aur Mistral** AI engines ka upyog karke human-like conversations karta hai.

---

## 🚀 Quick Deployment

Aap is bot ko niche diye gaye button par click karke turant **Heroku** par deploy kar sakte hain:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/rajayns42-design/Clonechatbot)

---

## ✨ Key Features

* 📥 **Unlimited Cloning:** Koi bhi user apna `/clone <token>` daal kar bot bana sakta hai.
* 🧠 **Multi-AI Engine:** Ek hi bot mein Gemini, Groq, aur Mistral ka power.
* 📢 **Owner-Only Broadcast:** Saare cloned bots aur unke groups mein ek saath message bhejien (Sirf Real Owner ke liye).
* 🛡️ **Powerful Admin Tools:** Ban, Mute, Promote, aur Adminlist jaise commands.
* 📊 **Clone Logger:** Jab bhi koi naya bot clone hoga, aapko report mil jayegi.
* 👋 **Stylish Welcome:** Naye members ke liye customizable aur stylish welcome message.
* 📂 **MongoDB Persistence:** Restart ke baad saare bots apne aap auto-start ho jayenge.

---

## ⚙️ Configuration (Env Vars)

Heroku par **Config Vars** mein ye values bharna zaroori hai:

| Variable | Description |
| :--- | :--- |
| `TOKEN` | Aapke Main Bot ka API Token (@BotFather). |
| `MONGO_URL` | MongoDB Atlas ki connection string. |
| `OWNER_ID` | Aapki numeric Telegram ID (Broadcast permission ke liye). |
| `CLONE_LOGGER` | Wo Group ID jahan naye clones ki report chahiye. |
| `API_ID` & `API_HASH` | Telegram API credentials (my.telegram.org). |
| `GEMINI_API_KEY` | Google AI Studio se mili API Key. |

---

## 📜 Bot Commands

### **For Users**
- `/start` - Bot ki info aur start message.
- `/clone <token>` - Apna khud ka bot clone karein.
- `/delclone <token>` - Apne cloned bot ko band karein.

### **For Admins (In Groups)**
- `/ban` - User ko ban karne ke liye.
- `/mute` - User ko chup karane ke liye.
- `/promote` - Kisi ko admin banane ke liye.

### **For Real Owner**
- `/broadcast` - (Reply to message) Saare clones ke groups mein message bhejne ke liye.

---

## 🛠 Manual Installation (VPS)

```bash
# Repository clone karein
git clone [https://github.com/rajayns42-design/Clonechatbot](https://github.com/yourusername/natkhat-ai)
cd natkhat-ai

# Requirements install karein
pip install -r requirements.txt

# Bot start karein
python3 main.py
