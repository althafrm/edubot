from flask import Flask, request, render_template, session, jsonify
from inference_engine import get_answer, learn

app = Flask(__name__)
app.secret_key = "edubot_secret_key"

@app.route("/")
def index():
    if "chat" not in session:
        session["chat"] = []
    return render_template("index.html", chat=session["chat"])

@app.route("/ask", methods=["POST"])
def ask():
    if "chat" not in session:
        session["chat"] = []

    data = request.json
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    bot_response = get_answer(user_input)
    session["chat"].append(("user", user_input))
    session["chat"].append(("bot", bot_response))
    session.modified = True
    return jsonify({"reply": bot_response})

@app.route("/teach", methods=["POST"])
def teach():
    data = request.json
    question = data.get("question", "").strip()
    answer = data.get("answer", "").strip()

    if not question or not answer:
        return jsonify({"error": "Missing question or answer"}), 400

    learn(question, answer)
    session["chat"].append(("user", question))
    session["chat"].append(("bot", "Thanks! I've learned that."))
    session.modified = True
    return jsonify({"reply": "Thanks! I've learned that."})

@app.route("/reset", methods=["POST"])
def reset_chat():
    session.pop("chat", None)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
