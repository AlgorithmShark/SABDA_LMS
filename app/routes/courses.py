from flask import Blueprint, g, request

from .. import db
from ..access import (course_or_404, is_enrolled, is_manager, lesson_or_404, require_access, require_manager)
from ..utils import (ApiError, auth_required, get_bool, get_choice, get_int, get_str, get_url, json_body, now_iso,
                    ok, optional_user, pagination)

bp = Blueprint("courses", __name__)

LEVELS = ("beginner", "intermediate", "advanced")
COURSE_COLS = "id,title,description,category_id,instructor_id,level,is_published,created_at,updated_at"


# ---------- helper ----------
def enrich(courses: list) -> list:
    """Tambahkan nama kategori, nama pengajar, jumlah pelajaran & siswa."""
    if not courses:
        return []
    ids = [c["id"] for c in courses]
    cats = {r["id"]: r["name"] for r in
            db.table("categories").select("id,name").in_("id", list({c["category_id"] for c in courses})).execute().data}
    teachers = {r["id"]: r["name"] for r in
                db.table("users").select("id,name").in_("id", list({c["instructor_id"] for c in courses})).execute().data}
    stats = {r["course_id"]: r for r in
             db.table("course_stats").select("course_id,lesson_count,student_count").in_("course_id", ids).execute().data}
    return [
        {
            **c,
            "category_name": cats.get(c["category_id"]),
            "instructor_name": teachers.get(c["instructor_id"]),
            "lesson_count": stats.get(c["id"], {}).get("lesson_count", 0),
            "student_count": stats.get(c["id"], {}).get("student_count", 0),
        }
        for c in courses
    ]


def course_payload(d: dict, partial: bool) -> dict:
    out = {}
    if not partial or "title" in d:
        out["title"] = get_str(d, "title", required=True, max_len=150, min_len=3)
    if not partial or "description" in d:
        out["description"] = get_str(d, "description", max_len=5000, default="")
    if not partial or "category_id" in d:
        cid = get_int(d, "category_id", required=True)
        if not db.get_by_id("categories", cid, "id"):
            raise ApiError("Kategori tidak ditemukan", 400)
        out["category_id"] = cid
    if not partial or "level" in d:
        out["level"] = get_choice(d, "level", LEVELS, default="beginner")
    if not partial or "is_published" in d:
        out["is_published"] = get_bool(d, "is_published", default=False)
    return out


def lesson_payload(d: dict, partial: bool) -> dict:
    out = {}
    if not partial or "title" in d:
        out["title"] = get_str(d, "title", required=True, max_len=150, min_len=3)
    if not partial or "content" in d:
        out["content"] = get_str(d, "content", max_len=20000, default="")
    if not partial or "video_url" in d:
        out["video_url"] = get_url(d, "video_url")
    if "position" in d:
        out["position"] = get_int(d, "position", required=True)
    return out


# ---------- courses ----------
@bp.get("/api/courses")
def list_courses():
    user = optional_user()
    scope = request.args.get("scope")
    q = db.table("courses").select(COURSE_COLS, count="exact")
    if scope in ("mine", "all"):
        if not user:
            raise ApiError("Token autentikasi diperlukan", 401)
        if user["role"] not in ("instructor", "admin") or (scope == "all" and user["role"] != "admin"):
            raise ApiError("Anda tidak memiliki akses ke resource ini", 403)
        if scope == "mine":
            q = q.eq("instructor_id", user["id"])
    else:
        q = q.eq("is_published", True)
    if request.args.get("category_id"):
        q = q.eq("category_id", get_int(request.args, "category_id"))
    if request.args.get("level"):
        q = q.eq("level", get_choice(request.args, "level", LEVELS))
    term = (request.args.get("q") or "").strip()
    if term:
        q = q.ilike("title", f"%{term[:100]}%")
    page, per_page, start, end = pagination()
    res = q.order("created_at", desc=True).range(start, end).execute()
    return ok(enrich(res.data), meta={"page": page, "per_page": per_page, "total": res.count or 0})


@bp.get("/api/courses/<int:course_id>")
def get_course(course_id):
    user = optional_user()
    course = course_or_404(course_id)
    if not course["is_published"] and not is_manager(user, course):
        raise ApiError("Kursus tidak ditemukan", 404)
    data = enrich([course])[0]
    lessons = db.table("lessons").select("id,title,position").eq("course_id", course_id).order("position").order("id").execute().data
    enrolled = is_enrolled(user, course_id)
    if enrolled:
        done = {r["lesson_id"] for r in db.table("lesson_progress").select("lesson_id").eq("user_id", user["id"]).execute().data}
        for lesson in lessons:
            lesson["is_completed"] = lesson["id"] in done
    data.update(lessons=lessons, is_enrolled=enrolled, can_manage=is_manager(user, course))
    return ok(data)


@bp.post("/api/courses")
@auth_required("instructor", "admin")
def create_course():
    d = json_body()
    payload = course_payload(d, partial=False)
    payload["instructor_id"] = g.user["id"]
    if g.user["role"] == "admin" and d.get("instructor_id") is not None:
        teacher = db.get_by_id("users", get_int(d, "instructor_id"), "id,role")
        if not teacher or teacher["role"] not in ("instructor", "admin"):
            raise ApiError("Pengajar tidak ditemukan", 400)
        payload["instructor_id"] = teacher["id"]
    row = db.table("courses").insert(payload).execute().data[0]
    return ok(enrich([row])[0], "Kursus berhasil ditambahkan", 201)


def _update_course(course_id, partial):
    course = course_or_404(course_id)
    require_manager(g.user, course)
    payload = course_payload(json_body(), partial)
    if not payload:
        raise ApiError("Tidak ada field yang diubah")
    payload["updated_at"] = now_iso()
    row = db.table("courses").update(payload).eq("id", course_id).execute().data[0]
    return ok(enrich([row])[0], "Kursus berhasil diperbarui")


@bp.put("/api/courses/<int:course_id>")
@auth_required("instructor", "admin")
def replace_course(course_id):
    return _update_course(course_id, partial=False)


@bp.patch("/api/courses/<int:course_id>")
@auth_required("instructor", "admin")
def patch_course(course_id):
    return _update_course(course_id, partial=True)


@bp.delete("/api/courses/<int:course_id>")
@auth_required("instructor", "admin")
def delete_course(course_id):
    require_manager(g.user, course_or_404(course_id))
    db.table("courses").delete().eq("id", course_id).execute()
    return ok(message="Kursus berhasil dihapus")


# ---------- lessons ----------
@bp.get("/api/courses/<int:course_id>/lessons")
@auth_required()
def list_lessons(course_id):
    course = course_or_404(course_id)
    require_access(g.user, course)
    rows = db.table("lessons").select("*").eq("course_id", course_id).order("position").order("id").execute().data
    return ok(rows)


@bp.post("/api/courses/<int:course_id>/lessons")
@auth_required("instructor", "admin")
def create_lesson(course_id):
    require_manager(g.user, course_or_404(course_id))
    payload = lesson_payload(json_body(), partial=False)
    if "position" not in payload:
        last = db.one(db.table("lessons").select("position").eq("course_id", course_id).order("position", desc=True).limit(1).execute())
        payload["position"] = (last["position"] if last else 0) + 1
    payload["course_id"] = course_id
    row = db.table("lessons").insert(payload).execute().data[0]
    return ok(row, "Pelajaran berhasil ditambahkan", 201)


@bp.get("/api/lessons/<int:lesson_id>")
@auth_required()
def get_lesson(lesson_id):
    lesson = lesson_or_404(lesson_id)
    course = course_or_404(lesson["course_id"])
    require_access(g.user, course)
    siblings = db.table("lessons").select("id").eq("course_id", course["id"]).order("position").order("id").execute().data
    ids = [r["id"] for r in siblings]
    i = ids.index(lesson_id)
    done = db.one(db.table("lesson_progress").select("id").eq("user_id", g.user["id"]).eq("lesson_id", lesson_id).limit(1).execute())
    lesson.update(
        course_title=course["title"],
        is_completed=done is not None,
        prev_lesson_id=ids[i - 1] if i > 0 else None,
        next_lesson_id=ids[i + 1] if i < len(ids) - 1 else None,
    )
    return ok(lesson)


def _update_lesson(lesson_id, partial):
    lesson = lesson_or_404(lesson_id)
    require_manager(g.user, course_or_404(lesson["course_id"]))
    payload = lesson_payload(json_body(), partial)
    if not payload:
        raise ApiError("Tidak ada field yang diubah")
    row = db.table("lessons").update(payload).eq("id", lesson_id).execute().data[0]
    return ok(row, "Pelajaran berhasil diperbarui")


@bp.put("/api/lessons/<int:lesson_id>")
@auth_required("instructor", "admin")
def replace_lesson(lesson_id):
    return _update_lesson(lesson_id, partial=False)


@bp.patch("/api/lessons/<int:lesson_id>")
@auth_required("instructor", "admin")
def patch_lesson(lesson_id):
    return _update_lesson(lesson_id, partial=True)


@bp.delete("/api/lessons/<int:lesson_id>")
@auth_required("instructor", "admin")
def delete_lesson(lesson_id):
    lesson = lesson_or_404(lesson_id)
    require_manager(g.user, course_or_404(lesson["course_id"]))
    db.table("lessons").delete().eq("id", lesson_id).execute()
    return ok(message="Pelajaran berhasil dihapus")
