from pathlib import Path
import pytest


def _make_file(tmp_path: Path, name="hello.txt", content="Hello"):
    f = tmp_path / name
    f.write_text(content)
    return f


def test_upload(client, tmp_path: Path):
    f = _make_file(tmp_path)
    with f.open("rb") as handle:
        resp = client.post(
            "/upload", files={"file": (f.name, handle, "text/plain")})
    assert resp.status_code == 201
    assert resp.json()["filename"] == f.name


def test_list(client, tmp_path: Path):
    test_upload(client, tmp_path)  # ensure at least one file
    resp = client.get("/list")
    assert any(row["filename"] == "hello.txt" for row in resp.json())


def test_download(client, tmp_path: Path):
    f = _make_file(tmp_path, content="XYZ")
    with f.open("rb") as handle:
        client.post("/upload", files={"file": (f.name, handle, "text/plain")})
    resp = client.get(f"/download/{f.name}")
    assert resp.content == b"XYZ"
    assert resp.headers["content-disposition"].endswith(f.name + '"')


def test_delete(client, tmp_path: Path):
    f = _make_file(tmp_path)
    with f.open("rb") as handle:
        client.post("/upload", files={"file": (f.name, handle, "text/plain")})
    resp = client.delete(f"/delete/{f.name}")
    assert resp.status_code == 204
    # now 404
    resp = client.get(f"/download/{f.name}")
    assert resp.status_code == 404


def test_conflict(client, tmp_path: Path):
    f = _make_file(tmp_path)
    for _ in range(2):
        with f.open("rb") as handle:
            r = client.post(
                "/upload", files={"file": (f.name, handle, "text/plain")})
    assert r.status_code == 409


def test_not_found(client):
    resp = client.delete("/delete/nope.txt")
    assert resp.status_code == 404
