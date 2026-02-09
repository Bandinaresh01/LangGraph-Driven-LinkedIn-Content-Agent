# server.py
from flask import Flask, render_template, request
from app import llm_workflow  # ✅ imports from app.py

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic", "").strip()

    if not topic:
        return render_template("index.html", content1="Please enter a topic.", content2="")

    try:
        content1, content2 = llm_workflow(topic)
        return render_template("index.html", content1=content1, content2=content2)
    except Exception as e:
        return render_template("index.html", content1="Error generating post.", content2=str(e))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
