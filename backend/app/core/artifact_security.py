"""HER AI — Artifact Security, File Signature Verification & Storage Isolation.

Enforces:
  - MIME type and magic byte signature verification to prevent spoofed files.
  - Per-user storage path isolation without executable permissions.
  - SHA-256 integrity checksum calculation.
  - Configurable file size limits.
  - Safe file deletion.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from uuid import UUID

from app.core.config import settings

# Recognized magic byte signatures
MAGIC_SIGNATURES: dict[str, list[bytes]] = {
    "application/pdf": [b"%PDF"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "audio/mpeg": [b"\xff\xfb", b"\xff\xf3", b"\xff\xf2", b"ID3"],
    "audio/wav": [b"RIFF"],
}

# Plaintext types verified via UTF-8 decoding check rather than binary header
TEXT_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "text/vtt",
    "application/x-subrip",
    "text/csv",
}

SAFE_FILENAME_RE = re.compile(r"[^a-zA-Z0-9_\-\.]")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and illegal characters."""
    base = os.path.basename(filename)
    safe = SAFE_FILENAME_RE.sub("_", base)
    if not safe or safe.startswith("."):
        safe = f"file_{safe}"
    return safe[:100]


def calculate_sha256(content: bytes) -> str:
    """Calculate SHA-256 checksum of raw file bytes."""
    return hashlib.sha256(content).hexdigest()


def validate_artifact_content(
    content: bytes,
    mime_type: str,
    max_size_bytes: int | None = None,
) -> None:
    """
    Validate artifact byte content against size and magic file signatures.
    Raises ValueError on violation.
    """
    limit = max_size_bytes or settings.ARTIFACT_MAX_FILE_SIZE_BYTES
    if len(content) == 0:
        raise ValueError("File content cannot be empty.")

    if len(content) > limit:
        raise ValueError(
            f"File size ({len(content)} bytes) exceeds maximum allowed limit ({limit} bytes)."
        )

    norm_mime = mime_type.lower().strip()

    # If it is a known binary type with magic bytes, check prefix
    if norm_mime in MAGIC_SIGNATURES:
        signatures = MAGIC_SIGNATURES[norm_mime]
        if not any(content.startswith(sig) for sig in signatures):
            raise ValueError(
                f"File content does not match expected magic signature for MIME type '{norm_mime}'."
            )
    elif norm_mime in TEXT_MIME_TYPES or norm_mime.startswith("text/"):
        # Ensure it is valid text
        try:
            content[:4096].decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(f"File marked as '{norm_mime}' contains invalid non-text characters.")
    else:
        raise ValueError(f"Unsupported MIME type: '{norm_mime}'.")


def get_user_artifact_dir(user_id: UUID) -> Path:
    """Get or create isolated storage directory for user artifacts."""
    base_dir = Path(settings.ARTIFACT_STORAGE_DIR)
    user_dir = base_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def save_artifact_file(
    user_id: UUID,
    filename: str,
    content: bytes,
    mime_type: str,
) -> tuple[str, str, int]:
    """
    Validates, saves file to user's isolated storage directory, and removes executable bits.
    Returns:
        (relative_storage_path, checksum_sha256, file_size_bytes)
    """
    validate_artifact_content(content, mime_type)
    checksum = calculate_sha256(content)
    safe_name = sanitize_filename(filename)

    user_dir = get_user_artifact_dir(user_id)
    target_path = user_dir / f"{checksum[:12]}_{safe_name}"

    # Write file securely
    target_path.write_bytes(content)

    # Set non-executable permissions (rw-r--r-- on POSIX, standard on Windows)
    try:
        os.chmod(target_path, 0o644)
    except OSError:
        pass

    # Return relative or canonical storage path string
    return str(target_path.as_posix()), checksum, len(content)


def delete_artifact_file(storage_path: str) -> bool:
    """Safely delete stored artifact file from disk."""
    if not storage_path:
        return False
    path = Path(storage_path)
    if path.exists() and path.is_file():
        try:
            path.unlink()
            return True
        except OSError:
            return False
    return False

