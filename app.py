import os
import requests
from flask import Flask, request

app = Flask(__name__)

PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "src123")

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

@app.route("/")
def home():
    return "SRC Print Bot is Running!"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received:", data)
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            msg_type = message["type"]

            if msg_type == "document":
                filename = message["document"]["filename"]
                reply = f"✅ SRC Print Received: {filename}\n\n🖨️ SRC - Bhubaneswar\nA4 B/W: Rs 3/page\nA4 Color: Rs 10/page\n\nYour print will be ready in 10 mins. Visit shop or type YES for delivery."
                send_whatsapp_message(from_number, reply)

            elif msg_type == "image":
                reply = f"✅ Photo received at SRC!\n\n🖨️ Print Rates:\n4x6: Rs 15\n5x7: Rs 25\n\nReply size & quantity."
                send_whatsapp_message(from_number, reply)

            else:
                reply = "Welcome to SRC Print Shop! 🖨️ Bhubaneswar\n\nSend your PDF / Photo here to print.\n\nRates:\nA4 B/W - Rs 3\nA4 Color - Rs 10\nPhoto 4x6 - Rs 15\n\nTiming: 8AM - 9PM"
                send_whatsapp_message(from_number, reply)
    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200
@app.route('/privacy-policy')
def privacy_policy():
    return "<h1>Privacy Policy - SRC Print Shop Bhubaneswar</h1><p>We respect privacy. We do not collect or store personal data. WhatsApp messages used only for print services. Contact gpjsrc@gmail.com to delete data. Deletion within 24 hours.</p>"

@app.route('/data-deletion')
def data_deletion():
    return "<h1>Data Deletion - SRC</h1><p>Email gpjsrc@gmail.com to delete your data.</p>"
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
