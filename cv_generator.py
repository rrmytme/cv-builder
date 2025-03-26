from flask import Flask, render_template
from utils import get_candidate_data, select_template, generate_pdf_from_html
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Define model
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    country = db.Column(db.String(50))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    education = db.Column(db.Text)
    certification = db.Column(db.Text)
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route("/")
def form():
    return render_template("cv_form.html")


@app.route("/generate_cv", methods=["POST"])
def generate_cv():
    data = get_candidate_data()
    selected_template = select_template(data["country"])

    rendered_html = render_template(selected_template, data=data)
    # Save data to database
    candidate = Candidate(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        country=data["country"],
        linkedin=data["linkedin"],
        github=data["github"],
        skills=data["skills"],
        experience=data["experience"],
        education=data["education"],
        certification=data["certification"],
        summary=data["summary"],
    )
    db.session.add(candidate)
    db.session.commit()

    # Select template based on country
    template_name = f"{data['country'].lower()}_cv.html"

    # Generate PDF
    pdf_path = generate_pdf_from_html(template_name, data)

    # Upload to S3
    # pdf_url = upload_to_s3(pdf_path)

    return render_template("result.html", rendered_html)


if __name__ == "__main__":
    app.run(debug=True)
