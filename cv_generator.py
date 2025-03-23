from flask import Flask, render_template, request, redirect, url_for
from app.utils import get_candidate_data, select_template, generate_pdf, upload_to_s3
import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
DB_PATH = "cv_generator.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()


# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS candidates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        phone TEXT,
                        country TEXT,
                        linkedin TEXT,
                        github TEXT,
                        skills TEXT,
                        experience TEXT,
                        education TEXT,
                        certification TEXT,
                        created_at TEXT
                    )"""
    )
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def form():
    return render_template("form.html")


@app.route("/generate_cv", methods=["POST"])
def generate_cv():
    data = get_candidate_data()
    selected_template = select_template(data["country"])

    rendered_html = render_template(selected_template, data=data)

    # Save data to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO candidates (name, email, phone, country, linkedin, github, skills, experience, education, certification, created_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["name"],
            data["email"],
            data["phone"],
            data["country"],
            data["linkedin"],
            data["github"],
            data["skills"],
            data["experience"],
            data["education"],
            data["certification"],
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    # Select template based on country
    template_name = f"{data['country'].lower()}_cv.html"

    # Generate PDF
    pdf_path = generate_pdf(template_name, data)

    # Upload to S3
    pdf_url = upload_to_s3(pdf_path)

    return render_template("result.html", pdf_url=pdf_url)


if __name__ == "__main__":
    app.run(debug=True)
