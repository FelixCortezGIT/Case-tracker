from database import db

class Case(db.Model):
    __tablename__ = "cases"

    case_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    transaction_amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    merchant_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    deadline_date = db.Column(db.Date)

    status_id = db.Column(db.Integer, db.ForeignKey("status.status_id"), nullable=False)

    status = db.relationship("Status")
