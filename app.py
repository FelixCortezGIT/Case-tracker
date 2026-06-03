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

# with app.app_context():
#     db.create_all()

# @app.route("/authors")
# def authors():
#     search = request.args.get("name", "")
#     if search:
#         authors = Author.query.filter(Author.name.ilike(f"%{search}%")).all()
#     else:
#         authors = Author.query.all()
#     return render_template("index.html", authors=authors)

if __name__ == "__main__":
    app.run(debug=True)
