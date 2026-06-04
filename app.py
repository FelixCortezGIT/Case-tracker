import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for

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

@app.route("/new_case", methods=["GET", "POST"])
def new_case():
    if request.method == "POST":
        new_case_record = Case(
            customer_name=request.form.get("customer_name"),
            card_number=request.form.get("card_number"),
            transaction_amount=request.form.get("transaction_amount"),
            transaction_date=request.form.get("transaction_date"),
            merchant_name=request.form.get("merchant_name"),
            deadline_date=request.form.get("deadline"),
            status_id=1
        )
        db.session.add(new_case_record)
        db.session.commit()
        return redirect(url_for("new_case"))
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

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
