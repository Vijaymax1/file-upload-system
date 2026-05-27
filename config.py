import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    ALLOWED_EXTENSIONS = {
        "image": {"png", "jpg", "jpeg", "gif", "webp", "svg"},
        "document": {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"},
    }

    # Flat set for quick lookup
    ALL_ALLOWED_EXTENSIONS = (
        ALLOWED_EXTENSIONS["image"] | ALLOWED_EXTENSIONS["document"]
    )

    # Metadata file path (JSON-based lightweight storage)
    METADATA_FILE = os.path.join(BASE_DIR, "uploads", ".metadata.json")
