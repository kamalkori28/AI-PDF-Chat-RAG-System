import re
import unicodedata


def sanitize_filename(filename: str) -> str:
    """Normalize user-provided filenames to a safe portable representation."""
    normalized = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode()
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", normalized).strip(".-")
    return normalized or "document.pdf"

