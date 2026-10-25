import os

from dotenv import load_dotenv
from flask import Flask, render_template, request

from recommend import recommend_problems

# Load GEMINI_API_KEY from .env before anything reads the environment.
load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = None
    ai_advice = None
    project_idea = ""

    if request.method == "POST":
        project_idea = request.form.get("project_idea", "").strip()

        if project_idea:
            recommendations, ai_advice = recommend_problems(project_idea)

    return render_template(
        "index.html",
        recommendations=recommendations,
        ai_advice=ai_advice,
        project_idea=project_idea,
    )


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )
