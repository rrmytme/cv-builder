import os
import boto3
from weasyprint import HTML
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app, request


def get_candidate_data():
    """
    Extracts candidate data from the submitted form and returns a structured dictionary.
    """
    return {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "country": request.form.get("country", "")
        .strip()
        .lower(),  # lowercase for template matching
        "linkedin": request.form.get("linkedin", "").strip(),
        "github": request.form.get("github", "").strip(),
        "skills": [
            skill.strip()
            for skill in request.form.get("skills", "").split(",")
            if skill.strip()
        ],
        "experience": request.form.get("experience", "").strip(),
        "education": request.form.get("education", "").strip(),
        "certification": request.form.get("certification", "").strip(),
    }


def select_template(country):
    """
    Returns the appropriate Jinja2 template filename based on the country input.
    Defaults to a generic template if no match is found.
    """
    templates = {
        "usa": "usa_template.html",
        "uk": "uk_template.html",
        "singapore": "singapore_template.html",
        "australia": "australia_template.html",
        "new zealand": "new_zealand_template.html",
    }

    # Normalize and match
    country = country.strip().lower()
    return templates.get(country, "generic_template.html")


def generate_pdf_from_html(html_content, output_filename):
    """
    Converts HTML content to PDF using WeasyPrint.
    Returns the path to the generated PDF file.
    """
    output_path = os.path.join(current_app.config["UPLOAD_FOLDER"], output_filename)
    HTML(string=html_content).write_pdf(output_path)
    return output_path


def upload_to_s3(file_path, bucket_name, s3_folder=None):
    """
    Uploads a file to AWS S3 and returns the public URL.
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),  # Default region
    )

    filename = secure_filename(os.path.basename(file_path))
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    s3_key = (
        f"{s3_folder}/{timestamp}_{filename}"
        if s3_folder
        else f"{timestamp}_{filename}"
    )

    s3.upload_file(
        file_path,
        bucket_name,
        s3_key,
        ExtraArgs={"ACL": "public-read", "ContentType": "application/pdf"},
    )

    public_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    return public_url
