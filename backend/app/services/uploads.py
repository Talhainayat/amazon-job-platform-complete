from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
ALLOWED_RESUME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
}


def resume_dir() -> Path:
    path = Path(settings.UPLOAD_DIR) / "resumes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_resume(file: UploadFile, candidate_id: int) -> tuple[str, str]:
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume must be a PDF, DOC, or DOCX file",
        )
    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_RESUME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported resume file type")

    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > settings.MAX_RESUME_BYTES:
        raise HTTPException(status_code=400, detail="Resume must be 5 MB or smaller")

    stored_name = f"candidate-{candidate_id}-{uuid4().hex}{suffix}"
    dest = resume_dir() / stored_name
    dest.write_bytes(data)
    return str(dest), filename
