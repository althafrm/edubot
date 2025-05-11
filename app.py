from flask import Flask, render_template, request, jsonify, session
from inference_engine import get_answer

app = Flask(__name__)
app.secret_key = "edubot_secret"

@app.route("/")
def home():
    if "chat" not in session:
        session["chat"] = []
    return render_template("index.html", chat=session["chat"])

@app.route("/ask", methods=["POST"])
def ask():
    if "chat" not in session:
        session["chat"] = []
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Please type something."})
    reply = get_answer(user_input)
    session["chat"].append(("user", user_input))
    session["chat"].append(("bot", reply))
    session.modified = True
    return jsonify({"reply": reply})

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("chat", None)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
