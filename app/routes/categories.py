from flask import Blueprint

from .. import db
from ..utils import ApiError, auth_required, get_str, json_body, ok

bp = Blueprint("categories", __name__, url_prefix="/api/categories")


def _get_or_404(category_id):
    row = db.get_by_id("categories", category_id)
    if not row:
        raise ApiError("Kategori tidak ditemukan", 404)
    return row


def _payload(d):
    return {
        "name": get_str(d, "name", required=True, max_len=80, min_len=2),
        "description": get_str(d, "description", max_len=500, default=""),
    }


@bp.get("")
def list_categories():
    rows = db.table("categories").select("*").order("name").execute().data
    return ok(rows)


@bp.get("/<int:category_id>")
def get_category(category_id):
    return ok(_get_or_404(category_id))


@bp.post("")
@auth_required("admin")
def create_category():
    row = db.table("categories").insert(_payload(json_body())).execute().data[0]
    return ok(row, "Kategori berhasil ditambahkan", 201)


@bp.put("/<int:category_id>")
@auth_required("admin")
def update_category(category_id):
    _get_or_404(category_id)
    row = db.table("categories").update(_payload(json_body())).eq("id", category_id).execute().data[0]
    return ok(row, "Kategori berhasil diperbarui")


@bp.delete("/<int:category_id>")
@auth_required("admin")
def delete_category(category_id):
    _get_or_404(category_id)
    db.table("categories").delete().eq("id", category_id).execute()
    return ok(message="Kategori berhasil dihapus")
