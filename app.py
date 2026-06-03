from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///corefix.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    device = db.Column(db.String(120), nullable=False)
    issue = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    service_type = db.Column(db.String(40), nullable=False)
    preferred_time = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default="New")

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    services = [
        "Screen Repairs",
        "Battery Replacement",
        "Charging Port Repairs",
        "Back Glass Repair",
        "Camera Repair",
        "Water Damage",
        "Speaker & Mic Repair",
        "Data Recovery",
    ]
    return render_template("index.html", services=services)

@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        ticket = Ticket(
            name=request.form["name"].strip(),
            phone=request.form["phone"].strip(),
            email=request.form["email"].strip(),
            device=request.form["device"].strip(),
            issue=request.form["issue"].strip(),
            description=request.form["description"].strip(),
            service_type=request.form["service_type"].strip(),
            preferred_time=request.form.get("preferred_time", "").strip(),
        )
        db.session.add(ticket)
        db.session.commit()
        flash(f"Ticket #{ticket.id} created successfully.", "success")
        return redirect(url_for("ticket_success", ticket_id=ticket.id))
    return render_template("book.html")

@app.route("/ticket/<int:ticket_id>")
def ticket_success(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template("ticket_success.html", ticket=ticket)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == os.environ.get("ADMIN_PASSWORD", "admin123"):
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Wrong password.", "error")
    if not session.get("admin"):
        return render_template("admin_login.html")
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template("admin.html", tickets=tickets)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/ticket/<int:ticket_id>/status", methods=["POST"])
def update_status(ticket_id):
    if not session.get("admin"):
        return redirect(url_for("admin"))
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = request.form["status"]
    db.session.commit()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)