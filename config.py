"""Application configuration."""
import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    CERT_FOLDER = os.path.join(BASE_DIR, "certificates")
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates_certificates")
    ZIP_FOLDER = os.path.join(BASE_DIR, "generated_zip")
    DB_PATH = os.path.join(BASE_DIR, "database", "history.db")
    ALLOWED_DATA_EXT = {"csv", "xlsx"}
    ALLOWED_IMG_EXT = {"png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@example.com")
    APP_URL = os.getenv("APP_URL", "http://127.0.0.1:5000")