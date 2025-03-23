from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Candidate(db.Model):
    __tablename__ = "cv_data"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    linkedin = db.Column(db.String(100))
    github = db.Column(db.String(100))
    skills = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)
    education = db.Column(db.Text, nullable=False)
    certification = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __init__(
        self,
        name,
        email,
        phone,
        country,
        linkedin,
        github,
        skills,
        experience,
        education,
        certification,
        created_at,
    ):
        self.name = name
        self.email = email
        self.phone = phone
        self.country = country
        self.linkedin = linkedin
        self.github = github
        self.skills = skills
        self.experience = experience
        self.education = education
        self.certification = certification
        self.created_at = created_at

    def __repr__(self):
        return f"<CvData {self.name}>"
