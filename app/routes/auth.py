from flask import Blueprint, g
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db
from ..utils import (ApiError, auth_required, get_email, get_password, get_str, json_body, make_token, now_iso,
                        ok, public_user)

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    d = json_body()
    name = get_str(d, "name", required=True, max_len=100, min_len=2)
    email = get_email(d)
    password = get_password(d)
    if db.one(db.table("users").select("id").eq("email", email).limit(1).execute()):
        raise ApiError("Email sudah terdaftar", 409)
    user = db.table("users").insert(
        {"name": name, "email": email, "password_hash": generate_password_hash(password), "role": "student"}
    ).execute().data[0]
    return ok({"user": public_user(user), "token": make_token(user)}, "Registrasi berhasil", 201)


@bp.post("/login")
def login():
    d = json_body()
    email = get_email(d)
    password = d.get("password")
    if not isinstance(password, str) or not password:
        raise ApiError("Field password wajib diisi")
    user = db.one(db.table("users").select("*").eq("email", email).limit(1).execute())
    if not user or not check_password_hash(user["password_hash"], password):
        raise ApiError("Email atau password salah", 401)
    return ok({"user": public_user(user), "token": make_token(user)}, "Login berhasil")


@bp.get("/me")
@auth_required()
def me():
    return ok(g.user)


@bp.patch("/me")
@auth_required()
def update_me():
    d = json_body()
    changes = {}
    name = get_str(d, "name", max_len=100, min_len=2)
    if name:
        changes["name"] = name
    if d.get("new_password") is not None:
        new_pw = get_password(d, "new_password")
        row = db.get_by_id("users", g.user["id"], "password_hash")
        current = d.get("current_password")
        if not isinstance(current, str) or not check_password_hash(row["password_hash"], current):
            raise ApiError("Password saat ini salah", 400)
        changes["password_hash"] = generate_password_hash(new_pw)
    if not changes:
        raise ApiError("Tidak ada field yang diubah")
    updated = db.table("users").update(changes).eq("id", g.user["id"]).execute().data[0]
    return ok(public_user(updated), "Profil berhasil diperbarui")
