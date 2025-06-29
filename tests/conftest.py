import pytest
from fastapi.testclient import TestClient

from app import database as _db
from app.main import app


class _FakePool:
    """Minimal asyncpg-like stub backed by an in-memory dict."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    # helpers
    def _insert(self, filename, mime, content):
        if filename in self._store:
            import asyncpg  # fake identical exception class
            raise asyncpg.UniqueViolationError()
        self._store[filename] = {"mime": mime, "content": content}

    # asyncpg surface
    async def execute(self, query: str, *args):
        if query.startswith("SELECT"):
            return "SELECT 1"
        if query.startswith("INSERT"):
            self._insert(*args)
            return "INSERT 0 1"
        if query.startswith("DELETE"):
            deleted = self._store.pop(args[0], None)
            return f"DELETE 0 {1 if deleted else 0}"

    async def fetchrow(self, _q, filename):
        rec = self._store.get(filename)
        if not rec:
            return None
        return {"content": rec["content"], "mime_type": rec["mime"]}

    async def fetch(self, _q):
        return [
            {
                "filename": k,
                "size": len(v["content"]),
                "uploaded_at": "2025-01-01T00:00:00",
            }
            for k, v in self._store.items()
        ]

    async def close(self): ...


@pytest.fixture(autouse=True)
def fake_db(monkeypatch):
    """Auto-patch every test so app.database.get_pool returns FakePool."""
    pool = _FakePool()

    async def _get_pool():
        return pool

    # patch both the database module & the alias imported in app.main
    monkeypatch.setattr(_db, "get_pool", _get_pool, raising=True)
    import app.main as _main
    monkeypatch.setattr(_main, "get_pool", _get_pool, raising=True)
    yield


@pytest.fixture
def client():
    """Fresh TestClient for every test after monkey-patching is applied."""
    return TestClient(app, raise_server_exceptions=True)
