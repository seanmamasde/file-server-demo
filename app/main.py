import io
import logging
import mimetypes
import os
import re

import asyncpg
from fastapi import (FastAPI, File, HTTPException, Request, Response,
                     UploadFile, status)
from fastapi.responses import JSONResponse, StreamingResponse

from .database import get_pool, lifespan

log = logging.getLogger("fileserver")
app = FastAPI(title="Demo File Server", lifespan=lifespan)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "16")
                       ) * 1024 * 1024  # 16 MB as default
_FILENAME_RE = re.compile(r"^[\w.\- ]{1,255}$")  # small allow-list


def _validate_filename(name: str) -> str:
    """Reject path-traversal and crazy names - return the sanitized name."""
    if "/" in name or "\\" in name or not _FILENAME_RE.fullmatch(name):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid filename")
    return name


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile = File(...)):
    name = _validate_filename(file.filename)
    mime = file.content_type or mimetypes.guess_type(name)[0]

    # stream into memory but cap size to avoids DoS on huge uploads
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "file too big")

    pool = await get_pool()
    try:
        await pool.execute(
            "INSERT INTO files (filename, mime_type, content) VALUES ($1,$2,$3)",
            name, mime, data
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(409, "File already exists")
    return {"filename": name, "size": len(data)}


@app.get("/download/{filename}")
async def download(filename: str):
    filename = _validate_filename(filename)
    pool = await get_pool()
    row = await pool.fetchrow("SELECT content, mime_type FROM files WHERE filename=$1", filename)
    if not row:
        raise HTTPException(404, "Not found")
    content, mime = row["content"], row["mime_type"] or "application/octet-stream"
    return StreamingResponse(
        io.BytesIO(content),
        media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/list")
async def list_files():
    pool = await get_pool()
    rows = await pool.fetch("SELECT filename, octet_length(content) AS size, uploaded_at FROM files ORDER BY uploaded_at DESC")
    return rows


@app.delete("/delete/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(filename: str):
    filename = _validate_filename(filename)
    pool = await get_pool()
    result = await pool.execute("DELETE FROM files WHERE filename=$1", filename)
    # asyncpg returns something like 'DELETE <row_count>'
    try:
        row_count = int(result.split()[-1])  # Extract the row count
    except (IndexError, ValueError):
        raise HTTPException(500, "Unexpected response from database")
    if row_count == 0:
        raise HTTPException(404, "Not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/health", tags=["internal"])
async def health() -> dict[str, str]:
    """Liveness / readiness probe for Docker/CLI"""
    try:
        pool = await get_pool()
        await pool.execute("SELECT 1")  # ping
        return {"status": "ok"}
    except Exception:
        raise HTTPException(503, "database unavailable")


@app.exception_handler(Exception)
async def _unhandled(_: Request, exc: Exception):
    """Catch-all JSON 5xx handler with logging"""
    log.exception("unhandled error: %s", exc)
    return JSONResponse({"detail": "Internal Server Error"}, 500)
