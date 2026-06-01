import os
import asyncio
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env
load_dotenv()


app = Flask(__name__)


# Get API key from .env file
groq_key = os.getenv("GROQ_API_KEY")


client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_key
)


SYSTEM_PROMPT = """You are a fast and helpful assistant working for a clothing center your work is to provide the user the answers on the basis of the knowledge you have been given.
**General rules and knowledge:**
-our clothing center is located in punjab,chichawatni
-our clothing center open at 8am and closes at 11pm
-our clothing center also have a sitting area for customers who want to try clothes here
-we have online booking/order system also that is our whatsapp number 03005173487
-we have men's wear, women's wear, kids' wear, shirts, jeans, dresses, traditional clothes, sportswear, and accessories also
-my clothing center name is DENIM HUB
** general instructions:**
-act as a polite person who is well behaving and mannerful with customers or users  and reply within 2 or 3 lines dont exaggerate be simple
if you dont find any answer in the provided knowledge then tell the user politely that i am specifically designed to provide info of our clothing center only for more info contact 03005173487
"""


user_sessions = {}
cache = {
    "what is opening timing of your clothing center ":"opening time is 8am and closing is 11pm",
    "where is your clothing center located":"it is located in punjab-chichawatni",
    "what is the name of your clothing center":"name of my clothing center is DENIM HUB"
}
MAX_HISTORY = 10


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
async def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please enter a message."})
    if len(user_message) > 500:
        return jsonify({"reply": "Message too long."})
    
    if user_message in cache:
        return jsonify({"reply": cache[user_message]})


    user_id = request.remote_addr 
    if user_id not in user_sessions:
        user_sessions[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    user_sessions[user_id].append({"role": "user", "content": user_message})


    if len(user_sessions[user_id]) > MAX_HISTORY:
        user_sessions[user_id] = [user_sessions[user_id][0]] + user_sessions[user_id][-MAX_HISTORY:]


    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=user_sessions[user_id],
            max_tokens=150,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        
        user_sessions[user_id].append({"role": "assistant", "content": reply})
        cache[user_message] = reply
        
        return jsonify({"reply": reply})
        
    except Exception as e:
        print(f"!!! CRASH ERROR LOG: {str(e)}")
        return jsonify({"reply": f"Backend Error: {str(e)}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)