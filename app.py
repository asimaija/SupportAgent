from flask import Flask, render_template, request, jsonify
from agents.support_agent import answer_question

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data.get("question", "")

    if not question:
        return jsonify({
            "answer": "Please enter a question."
        })

    answer = answer_question(question)

    return jsonify({
        "answer": answer
    })


if __name__ == "__main__":
    app.run(debug=True)