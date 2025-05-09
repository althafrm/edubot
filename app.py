# app.py
from flask import Flask, render_template, request
from inference_engine import process_input

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    reply = ""
    if request.method == "POST":
        user_input = request.form.get("user_input")
        reply = process_input(user_input)
    return render_template("index.html", reply=reply)

if __name__ == "__main__":
    app.run(debug=True)
