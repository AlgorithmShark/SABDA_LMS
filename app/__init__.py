from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from . import db
from .config import load_config
from .utils import ApiError, ok

HTTP_MESSAGES = {
    404: "Endpoint tidak ditemukan",
    405: "Method HTTP tidak diizinkan untuk endpoint ini",
    413: "Ukuran request terlalu besar (maksimal 1 MB)",
    415: "Content-Type harus application/json",
}

# Kode error PostgreSQL -> (status HTTP, pesan)
PG_ERRORS = {
    "23505": (409, "Data sudah ada (duplikat)"),
    "23503": (409, "Data terhubung dengan data lain sehingga tidak dapat diproses"),
    "23514": (400, "Input tidak memenuhi aturan database"),
    "22P02": (400, "Format input tidak valid"),
    "22003": (400, "Nilai angka di luar batas"),
}


def create_app(test_config: dict | None = None) -> Flask:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:  # python-dotenv hanya dipakai untuk development lokal
        pass

    app = Flask(__name__)
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)
    app.json.sort_keys = False
    app.json.ensure_ascii = False
    app.url_map.strict_slashes = False

    from .routes import auth, categories, courses, learning, users

    for module in (auth, categories, courses, learning, users):
        app.register_blueprint(module.bp)

    # ---------- halaman frontend ----------
    @app.get("/")
    def index():
        return render_template("index.html")

    # ---------- endpoint umum ----------
    @app.get("/api")
    def api_root():
        return ok({"name": "SABDA LMS API", "version": "1.0.0", "health": "/api/health"})

    @app.get("/api/health")
    def health():
        try:
            db.table("categories").select("id").limit(1).execute()
            return ok({"status": "ok", "database": "up"})
        except RuntimeError:
            return jsonify({"status": "error", "database": "not_configured"}), 503
        except Exception:
            app.logger.exception("Health check gagal")
            return jsonify({"status": "error", "database": "down"}), 503

    @app.get("/api/stats")
    def stats():
        def count(table, **filters):
            q = db.table(table).select("id", count="exact")
            for k, v in filters.items():
                q = q.eq(k, v)
            return q.limit(1).execute().count or 0

        return ok(
            {
                "courses": count("courses", is_published=True),
                "lessons": count("lessons"),
                "students": count("users", role="student"),
            }
        )

    # ---------- error handling ----------
    @app.errorhandler(ApiError)
    def handle_api_error(e):
        return jsonify({"error": e.message}), e.status

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify({"error": HTTP_MESSAGES.get(e.code, e.description)}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        code = getattr(e, "code", None)
        if isinstance(code, str) and code in PG_ERRORS:
            status, message = PG_ERRORS[code]
            return jsonify({"error": message}), status
        app.logger.exception("Unhandled error")
        if isinstance(e, RuntimeError):
            return jsonify({"error": "Konfigurasi server belum lengkap"}), 500
        return jsonify({"error": "Terjadi kesalahan pada server"}), 500

    # ---------- header keamanan & CORS ----------
    origins = [o.strip() for o in app.config["CORS_ORIGINS"].split(",") if o.strip()]

    @app.after_request
    def add_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.path.startswith("/api"):
            resp.headers["Cache-Control"] = "no-store"
            origin = request.headers.get("Origin")
            if origin and ("*" in origins or origin in origins):
                resp.headers["Access-Control-Allow-Origin"] = "*" if "*" in origins else origin
                resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                resp.headers["Vary"] = "Origin"
        return resp

    return app
