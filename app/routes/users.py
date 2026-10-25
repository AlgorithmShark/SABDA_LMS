"""Manajemen pengguna (khusus admin)."""
from flask import Blueprint, g, request

from .. import db
from ..utils import (ApiError, auth_required, get_choice, get_str, json_body, ok, pagination, PUBLIC_USER_COLS)

bp = Blueprint("users", __name__, url_prefix="/api/users")
ROLES = ("admin", "instructor", "student")


def _get_or_404(user_id):
    row = db.get_by_id("users", user_id, PUBLIC_USER_COLS)
    if not row:
        raise ApiError("Pengguna tidak ditemukan", 404)
    return row


@bp.get("")
@auth_required("admin")
def list_users():
    q = db.table("users").select(PUBLIC_USER_COLS, count="exact")
    if request.args.get("role"):
        q = q.eq("role", get_choice(request.args, "role", ROLES))
    page, per_page, start, end = pagination(default=20, maximum=100)
    res = q.order("id").range(start, end).execute()
    return ok(res.data, meta={"page": page, "per_page": per_page, "total": res.count or 0})


@bp.get("/<int:user_id>")
@auth_required("admin")
def get_user(user_id):
    return ok(_get_or_404(user_id))


@bp.patch("/<int:user_id>")
@auth_required("admin")
def update_user(user_id):
    _get_or_404(user_id)
    d = json_body()
    changes = {}
    if "name" in d:
        changes["name"] = get_str(d, "name", required=True, max_len=100, min_len=2)
    if "role" in d:
        changes["role"] = get_choice(d, "role", ROLES)
        if user_id == g.user["id"] and changes["role"] != "admin":
            raise ApiError("Anda tidak dapat menurunkan role akun Anda sendiri")
    if not changes:
        raise ApiError("Tidak ada field yang diubah")
    row = db.table("users").update(changes).eq("id", user_id).execute().data[0]
    return ok({k: row[k] for k in PUBLIC_USER_COLS.split(",")}, "Pengguna berhasil diperbarui")


@bp.delete("/<int:user_id>")
@auth_required("admin")
def delete_user(user_id):
    _get_or_404(user_id)
    if user_id == g.user["id"]:
        raise ApiError("Anda tidak dapat menghapus akun Anda sendiri")
    db.table("users").delete().eq("id", user_id).execute()
    return ok(message="Pengguna berhasil dihapus")
