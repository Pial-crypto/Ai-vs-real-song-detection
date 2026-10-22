"""File storage abstraction (local filesystem / S3-compatible)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, List, Optional

from backend.app.config import get_settings
from backend.app.logging_config import get_logger

logger = get_logger("app.services.file_storage")


@dataclass
class StoredFile:
    id: str
    path: str
    size: int
    content_type: Optional[str] = None


class LocalFileStorage:
    def __init__(self, base_dir: str = "./storage") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, filename: Optional[str] = None, content_type: Optional[str] = None) -> StoredFile:
        file_id = str(uuid.uuid4())
        ext = Path(filename).suffix if filename else ""
        dest = self.base_dir / f"{file_id}{ext}"
        dest.write_bytes(data)
        logger.info("File stored", extra={"id": file_id, "size": len(data)})
        return StoredFile(id=file_id, path=str(dest), size=len(data), content_type=content_type)

    def save_stream(self, stream: BinaryIO, filename: Optional[str] = None, content_type: Optional[str] = None) -> StoredFile:
        return self.save(stream.read(), filename=filename, content_type=content_type)

    def load(self, file_id: str) -> Optional[bytes]:
        for p in self.base_dir.glob(f"{file_id}*"):
            return p.read_bytes()
        return None

    def delete(self, file_id: str) -> bool:
        for p in self.base_dir.glob(f"{file_id}*"):
            p.unlink()
            return True
        return False

    def exists(self, file_id: str) -> bool:
        return any(self.base_dir.glob(f"{file_id}*"))

    def list_files(self) -> List[StoredFile]:
        out = []
        for p in self.base_dir.iterdir():
            if p.is_file():
                out.append(StoredFile(id=p.stem, path=str(p), size=p.stat().st_size))
        return out

    def total_size(self) -> int:
        return sum(p.stat().st_size for p in self.base_dir.iterdir() if p.is_file())

    def cleanup_older_than(self, days: int) -> int:
        import time

        cutoff = time.time() - days * 86400
        removed = 0
        for p in self.base_dir.iterdir():
            if p.is_file() and p.stat().st_mtime < cutoff:
                p.unlink()
                removed += 1
        return removed


def get_file_storage() -> LocalFileStorage:
    settings = get_settings()
    base = getattr(settings, "storage_dir", "./storage")
    return LocalFileStorage(base_dir=base)
