from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile


MAX_IMAGE_SIZE = 5 * 1024 * 1024
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
