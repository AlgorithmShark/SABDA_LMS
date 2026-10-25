"""Akses database Supabase (PostgREST) lewat client resmi supabase-py."""
from flask import current_app

_client = None


def get_client():
    global _client
    if _client is None:
        url = current_app.config.get("SUPABASE_URL")
        key = current_app.config.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY belum diatur")
        from supabase import create_client  # import lazy agar cold start ringan

        _client = create_client(url, key)
    return _client


def table(name: str):
    return get_client().table(name)


def one(result):
    """Ambil baris pertama dari hasil query, atau None."""
    rows = result.data or []
    return rows[0] if rows else None


def get_by_id(name: str, row_id: int, cols: str = "*"):
    return one(table(name).select(cols).eq("id", row_id).limit(1).execute())
