import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

class Case(db.Model):
    __tablename__ = "cases"
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(25), nullable=False)
    transaction_amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    merchant_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    deadline_date = db.Column(db.Date)

@app.route("/")
def home():
    return "home page"

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
