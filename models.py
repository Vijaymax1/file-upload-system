import json
import os
from datetime import datetime


class FileMetadataStore:
    """
    Lightweight JSON-based metadata store.
    Manages file records: original name, stored name, upload time, size, type.
    """

    def __init__(self, metadata_file: str):
        self.metadata_file = metadata_file
        self._ensure_file()

    def _ensure_file(self):
        """Create the metadata file if it doesn't exist."""
        if not os.path.exists(self.metadata_file):
            self._write({})

    def _read(self) -> dict:
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _write(self, data: dict):
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def add(self, file_id: str, original_name: str, stored_name: str, size: int, file_type: str):
        """Save metadata for a newly uploaded file."""
        data = self._read()
        data[file_id] = {
            "id": file_id,
            "original_name": original_name,
            "stored_name": stored_name,
            "size": size,
            "file_type": file_type,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        self._write(data)
        return data[file_id]

    def get_all(self) -> list:
        """Return all file records sorted by upload time (newest first)."""
        data = self._read()
        records = list(data.values())
        records.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
        return records

    def get(self, file_id: str) -> dict | None:
        """Return a single file record by ID."""
        data = self._read()
        return data.get(file_id)

    def delete(self, file_id: str) -> bool:
        """Remove a file record by ID. Returns True if found and deleted."""
        data = self._read()
        if file_id in data:
            del data[file_id]
            self._write(data)
            return True
        return False
