import re
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from . import db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
PUBLIC_USER_FIELDS = ("id", "name", "email", "role", "created_at")
PUBLIC_USER_COLS = ",".join(PUBLIC_USER_FIELDS)


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------- response ----------
def ok(data=None, message=None, status=200, **extra):
    body = {}
    if message:
        body["message"] = message
    if data is not None:
        body["data"] = data
    body.update(extra)
    return jsonify(body), status


def public_user(user: dict) -> dict:
    return {k: user[k] for k in PUBLIC_USER_FIELDS if k in user}


# ---------- input validation ----------
def json_body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("Body harus berupa JSON object")
    return data


def get_str(data, key, *, required=False, max_len=255, min_len=0, default=None):
    if data.get(key) is None:
        if required:
            raise ApiError(f"Field {key} wajib diisi")
        return default
    val = data[key]
    if not isinstance(val, str):
        raise ApiError(f"Field {key} harus berupa teks")
    val = val.strip()
    if required and not val:
        raise ApiError(f"Field {key} wajib diisi")
    if len(val) > max_len:
        raise ApiError(f"Field {key} maksimal {max_len} karakter")
    if val and len(val) < min_len:
        raise ApiError(f"Field {key} minimal {min_len} karakter")
    return val


def get_int(data, key, *, required=False, min_value=1, default=None):
    if data.get(key) is None:
        if required:
            raise ApiError(f"Field {key} wajib diisi")
        return default
    val = data[key]
    if isinstance(val, bool) or not (isinstance(val, int) or (isinstance(val, str) and val.strip().lstrip("-").isdigit())):
        raise ApiError(f"Field {key} harus berupa angka bulat")
    val = int(val)
    if val < min_value:
        raise ApiError(f"Field {key} minimal {min_value}")
    return val


def get_bool(data, key, default=None):
    if data.get(key) is None:
        return default
    if not isinstance(data[key], bool):
        raise ApiError(f"Field {key} harus berupa true/false")
    return data[key]


def get_choice(data, key, choices, default=None):
    val = get_str(data, key, default=default)
    if val is not None and val not in choices:
        raise ApiError(f"Field {key} harus salah satu dari: {', '.join(choices)}")
    return val


def get_email(data, key="email"):
    email = get_str(data, key, required=True, max_len=254).lower()
    if not EMAIL_RE.match(email):
        raise ApiError("Format email tidak valid")
    return email


def get_password(data, key="password"):
    pw = data.get(key)
    if not isinstance(pw, str) or not pw:
        raise ApiError(f"Field {key} wajib diisi")
    if len(pw) < 8:
        raise ApiError("Password minimal 8 karakter")
    if len(pw) > 128:
        raise ApiError("Password maksimal 128 karakter")
    return pw


def get_url(data, key):
    val = get_str(data, key, max_len=500)
    if val and not URL_RE.match(val):
        raise ApiError(f"Field {key} harus berupa URL http/https yang valid")
    return val or None


def pagination(default=12, maximum=50):
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", default)), 1), maximum)
    except ValueError:
        raise ApiError("Parameter page/per_page harus berupa angka")
    start = (page - 1) * per_page
    return page, per_page, start, start + per_page - 1


# ---------- auth ----------
def make_token(user: dict) -> str:
    secret = current_app.config["JWT_SECRET"]
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET harus diisi minimal 32 karakter")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "role": user["role"],
        "iat": now,
        "exp": now + timedelta(hours=current_app.config["JWT_EXPIRES_HOURS"]),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _user_from_request(strict: bool):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer ") or len(header) < 8:
        if strict:
            raise ApiError("Token autentikasi diperlukan", 401)
        return None
    try:
        payload = jwt.decode(header[7:].strip(), current_app.config["JWT_SECRET"], algorithms=["HS256"])
        user = db.get_by_id("users", int(payload["sub"]), PUBLIC_USER_COLS)
    except jwt.ExpiredSignatureError:
        if strict:
            raise ApiError("Token sudah kedaluwarsa, silakan login ulang", 401)
        return None
    except (jwt.InvalidTokenError, KeyError, ValueError):
        if strict:
            raise ApiError("Token tidak valid", 401)
        return None
    if not user and strict:
        raise ApiError("Akun tidak ditemukan", 401)
    return user


def optional_user():
    return _user_from_request(strict=False)


def auth_required(*roles):
    """Decorator: wajib login, dan (opsional) hanya untuk role tertentu."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = _user_from_request(strict=True)
            if roles and user["role"] not in roles:
                raise ApiError("Anda tidak memiliki akses ke resource ini", 403)
            g.user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator
