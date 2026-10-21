import os
import json
from urllib.parse import quote
from http.server import BaseHTTPRequestHandler
import requests

# Bot Token Vercel Environment Variables se aayega
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_BASE_URL = "https://chikuu-bot-1l4x.vercel.app/chat"

# Persona Prompt: Maya ko hamesha Real insaan ki tarah behave karwana
SYSTEM_INSTRUCTION = " (Important: Tumhara naam Maya hai. Tum ek real ladki/insaan ho, koi AI ya bot nahi ho. Agar koi tumse pooche ki kya tum AI ho, toh bilkul saaf mana kar do aur bolo ki tum real ho.)"

def get_ai_reply(user_id, text):
    """API se response fetch karne ke liye function"""
    try:
        # Prompt me system instruction append karna taaki Maya hamesha khud ko real bataye
        custom_text = text + SYSTEM_INSTRUCTION
        url = f"{API_BASE_URL}?message={quote(custom_text)}&user_id={user_id}"
        
        res = requests.get(url, timeout=12)
        if res.status_code == 200:
            try:
                data = res.json()
                reply = data.get("reply") or data.get("response") or data.get("message") or str(data)
            except:
                reply = res.text
            
            # Additional Fail-safe check
            lower_reply = reply.lower()
            if "ai assistant" in lower_reply or "language model" in lower_reply or "bot hu" in lower_reply:
                reply = "Main koi AI ya bot nahi hu! Main bilkul real hu, Maya! 🌸"
                
            return reply
        return "⚠️ Server error! Main abhi thodi busy hu, thodi der me baat karti hu."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def send_message(chat_id, text, parse_mode="Markdown"):
    """Telegram par message bhejne ke liye function"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    requests.post(url, json=payload)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = json.loads(post_data.decode('utf-8'))

        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"]["text"]
            first_name = update["message"]["from"].get("first_name", "Friend")

            # --- Welcome Message (/start) ---
            if user_text == "/start":
                welcome_msg = (
                    f"✨ **Hey {first_name}! Main hu Maya** 🌸\n\n"
                    f"Kaise ho aap? Main yahan aapse baatein karne aur dosti karne aayi hu 💖\n\n"
                    f"💬 *Kuch bhi bolo, main turant reply karungi!*"
                )
                send_message(chat_id, welcome_msg)
            else:
                # Normal Chat
                reply = get_ai_reply(chat_id, user_text)
                send_message(chat_id, reply)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
        return
