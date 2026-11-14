from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile


MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_VIDEO_SIZE = 50 * 1024 * 1024
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"


def _image_extension(content: bytes) -> str:
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return ".webp"
    raise HTTPException(
        status_code=400,
        detail="Formato de imagem inválido. Use JPG, PNG, GIF ou WebP.",
    )


def _media_extension_and_type(content: bytes, content_type: str = "") -> tuple[str, str]:
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png", "IMAGEM"
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg", "IMAGEM"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return ".gif", "IMAGEM"
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return ".webp", "IMAGEM"

    if len(content) >= 12 and content[4:8] == b"ftyp":
        ext = ".mov" if "quicktime" in content_type else ".mp4"
        return ext, "VIDEO"
    if content.startswith(b"\x1a\x45\xdf\xa3"):
        return ".webm", "VIDEO"

    raise HTTPException(
        status_code=400,
        detail="Formato inválido. Envie imagens (JPG, PNG, GIF, WebP) ou vídeos (MP4, WebM, MOV).",
    )


async def store_image(
    image: UploadFile,
    category: str,
) -> tuple[str, Path]:
    content = await image.read(MAX_IMAGE_SIZE + 1)
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="A imagem deve ter no máximo 5 MB.",
        )
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Selecione uma imagem para enviar.",
        )

    extension = _image_extension(content)
    filename = f"{uuid4().hex}{extension}"
    category_dir = UPLOAD_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    file_path = category_dir / filename
    file_path.write_bytes(content)
    return f"/uploads/{category}/{filename}", file_path


async def store_media(
    media: UploadFile,
    category: str,
) -> tuple[str, str, Path]:
    content = await media.read(MAX_VIDEO_SIZE + 1)
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Selecione uma imagem ou vídeo válido.",
        )

    extension, media_type = _media_extension_and_type(content, media.content_type or "")

    if media_type == "IMAGEM" and len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="A imagem deve ter no máximo 5 MB.",
        )
    if media_type == "VIDEO" and len(content) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=413,
            detail="O vídeo deve ter no máximo 50 MB.",
        )

    filename = f"{uuid4().hex}{extension}"
    category_dir = UPLOAD_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    file_path = category_dir / filename
    file_path.write_bytes(content)
    return f"/uploads/{category}/{filename}", media_type, file_path

def remove_stored_media(media_url: str | None) -> None:
    if not media_url or not media_url.startswith("/uploads/"):
        return
    relative_path = media_url.removeprefix("/uploads/")
    file_path = (UPLOAD_DIR / relative_path).resolve()
    if UPLOAD_DIR.resolve() in file_path.parents and file_path.is_file():
        file_path.unlink(missing_ok=True)