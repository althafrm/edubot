from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
from inference_engine import get_answer

app = Flask(__name__)
app.secret_key = "edubot_secret"

@app.route("/")
def home():
    if "chat" not in session:
        session["chat"] = []
    current_time = datetime.now().strftime("%H:%M")
    return render_template("index.html", chat=session["chat"], current_time=current_time)

@app.route("/ask", methods=["POST"])
def ask():
    if "chat" not in session:
        session["chat"] = []
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Please type something."})
    reply = get_answer(user_input)
    timestamp = datetime.now().strftime("%H:%M")
    session["chat"].append(("user", user_input, timestamp))
    session["chat"].append(("bot", reply, timestamp))
    session.modified = True
    return jsonify({"reply": reply})

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("chat", None)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
