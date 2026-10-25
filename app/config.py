import os


def load_config() -> dict:
    """Baca konfigurasi dari environment variables (tidak ada secret di kode)."""
    return {
        "SUPABASE_URL": os.getenv("SUPABASE_URL", "").strip(),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip(),
        "JWT_SECRET": os.getenv("JWT_SECRET", "").strip(),
        "JWT_EXPIRES_HOURS": int(os.getenv("JWT_EXPIRES_HOURS", "24")),
        "CORS_ORIGINS": os.getenv("CORS_ORIGINS", "*"),
        "MAX_CONTENT_LENGTH": 1 * 1024 * 1024,  # 1 MB
        "SEND_FILE_MAX_AGE_DEFAULT": 86400,
    }
