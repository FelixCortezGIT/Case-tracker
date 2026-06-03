import os
from dotenv import load_dotenv
from flask import Flask, render_template, request

from database import db
from model.case import Case
from model.status import Status
from model.user import User

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)

@app.route("/")
def home():
    return "home page"

@app.route("/new_case")
def new_case():
    return render_template("new_case.html")

@app.route("/case_detail")
def case_detail():
    return render_template("case_detail.html")

@app.route("/letter_ques")
def letter_queue():
    return render_template("letter_ques.html")

@app.route("/chaser_ques")
def chaser_queue():
    return render_template("chaser_ques.html")

# @app.route("/authors")
# def authors():
#     search = request.args.get("name", "")
#     if search:
#         authors = Author.query.filter(Author.name.ilike(f"%{search}%")).all()
#     else:
#         authors = Author.query.all()
#     return render_template("index.html", authors=authors)

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
