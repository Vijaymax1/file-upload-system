import os
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    abort,
)
from werkzeug.utils import secure_filename

from models import FileMetadataStore

bp = Blueprint("main", __name__)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _get_store() -> FileMetadataStore:
    return FileMetadataStore(current_app.config["METADATA_FILE"])


def _allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALL_ALLOWED_EXTENSIONS"]


def _classify_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    cfg = current_app.config["ALLOWED_EXTENSIONS"]
    if ext in cfg["image"]:
        return "image"
    if ext in cfg["document"]:
        return "document"
    return "other"


def _human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def _format_dt(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%b %d, %Y  %H:%M UTC")
    except Exception:
        return iso_str


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@bp.route("/")
def index():
    store = _get_store()
    files = store.get_all()

    # Enrich records for the template
    for f in files:
        f["size_human"] = _human_size(f.get("size", 0))
        f["uploaded_at_fmt"] = _format_dt(f.get("uploaded_at", ""))
        ext = f.get("stored_name", "").rsplit(".", 1)[-1].lower()
        f["ext"] = ext

    return render_template("index.html", files=files)


@bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file part in the request.", "danger")
        return redirect(url_for("main.index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("main.index"))

    if not _allowed_file(file.filename):
        flash(
            "File type not allowed. Accepted: images (PNG, JPG, GIF, WEBP, SVG) "
            "and documents (PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, CSV).",
            "danger",
        )
        return redirect(url_for("main.index"))

    # Build a collision-proof stored filename
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit(".", 1)[-1].lower()
    file_id = uuid.uuid4().hex
    stored_name = f"{file_id}.{ext}"

    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name)
    file.save(save_path)

    size = os.path.getsize(save_path)
    file_type = _classify_type(original_name)

    store = _get_store()
    store.add(
        file_id=file_id,
        original_name=original_name,
        stored_name=stored_name,
        size=size,
        file_type=file_type,
    )

    flash(f'"{original_name}" uploaded successfully!', "success")
    return redirect(url_for("main.index"))


@bp.route("/download/<file_id>")
def download(file_id: str):
    store = _get_store()
    record = store.get(file_id)

    if not record:
        abort(404)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    stored_name = record["stored_name"]

    # Security: make sure the file actually lives in the upload folder
    safe_path = os.path.realpath(os.path.join(upload_folder, stored_name))
    if not safe_path.startswith(os.path.realpath(upload_folder)):
        abort(403)

    return send_from_directory(
        upload_folder,
        stored_name,
        as_attachment=True,
        download_name=record["original_name"],
    )


@bp.route("/preview/<file_id>")
def preview(file_id: str):
    """Serve image files inline for preview (no attachment header)."""
    store = _get_store()
    record = store.get(file_id)

    if not record or record.get("file_type") != "image":
        abort(404)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    stored_name = record["stored_name"]

    safe_path = os.path.realpath(os.path.join(upload_folder, stored_name))
    if not safe_path.startswith(os.path.realpath(upload_folder)):
        abort(403)

    return send_from_directory(upload_folder, stored_name)


@bp.route("/delete/<file_id>", methods=["POST"])
def delete(file_id: str):
    store = _get_store()
    record = store.get(file_id)

    if not record:
        flash("File not found.", "warning")
        return redirect(url_for("main.index"))

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, record["stored_name"])

    # Remove physical file
    if os.path.exists(file_path):
        os.remove(file_path)

    # Remove metadata record
    store.delete(file_id)

    flash(f'"{record["original_name"]}" deleted.', "info")
    return redirect(url_for("main.index"))
