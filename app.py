import os
from collections import deque
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("DEBUG → API KEY:", api_key)   # 👈 IMPORTANT

client = Groq(api_key=api_key)

# Short-term conversation memory
memory = deque(maxlen=20)

# Long-term user facts
user_profile = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    memory.append({"role": "user", "content": user_message})

    # ---- Simple fact extraction (name example) ----
    msg_lower = user_message.lower()

    if "i am" in msg_lower:
        name = user_message.lower().split("i am")[-1].strip()
        user_profile["name"] = name

    if "my name is" in msg_lower:
        name = user_message.lower().split("my name is")[-1].strip()
        user_profile["name"] = name

    # ---- Build system context from remembered facts ----
    system_context = ""

    if "name" in user_profile:
        system_context += f"The user's name is {user_profile['name']}.\n"

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_context},
            *list(memory)
        ]
    )

    bot_reply = completion.choices[0].message.content

    memory.append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True, port=5001)