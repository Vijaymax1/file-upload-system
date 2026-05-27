# FileVault — Flask File Upload System

A production-ready Flask application for secure local file uploads, listing, downloading, and deletion.

---

## Features

- **Drag-and-drop** or click-to-browse file upload
- **Client-side validation** before submission (file type + size)
- **Image thumbnail preview** before and after upload
- **File listing** with name, size, upload time, type badge
- **Secure download** with original filename restored
- **Delete** with confirmation dialog
- **UUID-based storage** prevents filename collisions
- **Path traversal protection** on all file routes
- **JSON metadata store** — no database required
- **16 MB** upload limit (configurable)

---

## Supported File Types

| Category  | Extensions                                          |
|-----------|-----------------------------------------------------|
| Images    | PNG, JPG, JPEG, GIF, WEBP, SVG                      |
| Documents | PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, CSV     |

---

## Project Structure

```
file-upload-system/
├── app.py              # Application factory
├── config.py           # All configuration constants
├── models.py           # JSON-based file metadata store
├── routes.py           # All Flask routes (upload, download, delete, list)
├── requirements.txt    # Python dependencies
├── uploads/            # Uploaded files (auto-created on first run)
│   └── .metadata.json  # Auto-generated metadata store
├── templates/
│   └── index.html      # Single-page UI (Jinja2)
└── static/
    ├── css/style.css   # Industrial dark UI
    └── js/main.js      # Drag-drop, preview, form logic
```

---

## Quick Start

### 1. Clone / copy the project

```bash
cd file-upload-system
```

### 2. Create and activate a virtual environment (recommended)

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

### 5. Open in your browser

```
http://localhost:5000
```

---

## Configuration

All settings are in `config.py`:

| Setting                | Default          | Description                        |
|------------------------|------------------|------------------------------------|
| `SECRET_KEY`           | dev key          | Override via `SECRET_KEY` env var  |
| `UPLOAD_FOLDER`        | `./uploads`      | Where files are stored on disk     |
| `MAX_CONTENT_LENGTH`   | 16 MB            | Max upload size                    |
| `ALLOWED_EXTENSIONS`   | images + docs    | Accepted file types                |

---

## Security Notes

- **Path traversal**: All download/preview routes call `os.path.realpath` and verify the resolved path stays inside `UPLOAD_FOLDER`.
- **Filename sanitisation**: `werkzeug.utils.secure_filename` strips dangerous characters from the original name.
- **Collision prevention**: Files are stored as `<uuid_hex>.<ext>` — the original name is kept only in metadata.
- **Type validation**: Validated both on the client (JS) and server (extension whitelist).
- **No authentication** is included by design (as specified). For production, add Flask-Login or similar.

---

## Running in Production

For a real deployment, swap the dev server for Gunicorn:

```bash
pip install gunicorn
gunicorn "app:create_app()" -w 4 -b 0.0.0.0:8000
```

Also set a strong `SECRET_KEY` environment variable:

```bash
export SECRET_KEY="your-very-long-random-secret-key"
```
