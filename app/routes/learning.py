"""Pendaftaran siswa ke kursus dan pelacakan progres belajar."""
from flask import Blueprint, g

from .. import db
from ..access import (course_or_404, course_progress, is_enrolled, lesson_or_404, require_manager)
from ..utils import ApiError, auth_required, ok
from .courses import enrich

bp = Blueprint("learning", __name__)


@bp.post("/api/courses/<int:course_id>/enroll")
@auth_required("student")
def enroll(course_id):
    course = course_or_404(course_id)
    if not course["is_published"]:
        raise ApiError("Kursus tidak ditemukan", 404)
    if is_enrolled(g.user, course_id):
        raise ApiError("Anda sudah terdaftar di kursus ini", 409)
    row = db.table("enrollments").insert({"user_id": g.user["id"], "course_id": course_id}).execute().data[0]
    return ok(row, "Berhasil mendaftar ke kursus", 201)


@bp.delete("/api/courses/<int:course_id>/enroll")
@auth_required("student")
def unenroll(course_id):
    course_or_404(course_id)
    if not is_enrolled(g.user, course_id):
        raise ApiError("Anda belum terdaftar di kursus ini", 404)
    lesson_ids = [r["id"] for r in db.table("lessons").select("id").eq("course_id", course_id).execute().data]
    if lesson_ids:
        db.table("lesson_progress").delete().eq("user_id", g.user["id"]).in_("lesson_id", lesson_ids).execute()
    db.table("enrollments").delete().eq("user_id", g.user["id"]).eq("course_id", course_id).execute()
    return ok(message="Anda keluar dari kursus")


@bp.get("/api/enrollments/me")
@auth_required()
def my_enrollments():
    rows = db.table("enrollments").select("course_id,enrolled_at").eq("user_id", g.user["id"]).order("enrolled_at", desc=True).execute().data
    if not rows:
        return ok([])
    ids = [r["course_id"] for r in rows]
    courses = {c["id"]: c for c in enrich(db.table("courses").select("*").in_("id", ids).execute().data)}
    lessons = db.table("lessons").select("id,course_id").in_("course_id", ids).execute().data
    done = {r["lesson_id"] for r in db.table("lesson_progress").select("lesson_id").eq("user_id", g.user["id"]).execute().data}
    out = []
    for r in rows:
        c = courses.get(r["course_id"])
        if not c:
            continue
        mine = [l["id"] for l in lessons if l["course_id"] == c["id"]]
        completed = len([i for i in mine if i in done])
        c["enrolled_at"] = r["enrolled_at"]
        c["progress"] = {"completed": completed, "total": len(mine),
                         "percent": round(completed * 100 / len(mine)) if mine else 0}
        out.append(c)
    return ok(out)


@bp.get("/api/courses/<int:course_id>/students")
@auth_required("instructor", "admin")
def course_students(course_id):
    require_manager(g.user, course_or_404(course_id))
    enr = db.table("enrollments").select("user_id,enrolled_at").eq("course_id", course_id).order("enrolled_at").execute().data
    if not enr:
        return ok([])
    users = {u["id"]: u for u in db.table("users").select("id,name,email").in_("id", [e["user_id"] for e in enr]).execute().data}
    lesson_ids = [r["id"] for r in db.table("lessons").select("id").eq("course_id", course_id).execute().data]
    done = db.table("lesson_progress").select("user_id,lesson_id").in_("lesson_id", lesson_ids).execute().data if lesson_ids else []
    out = []
    for e in enr:
        u = users.get(e["user_id"])
        if not u:
            continue
        completed = len([d for d in done if d["user_id"] == u["id"]])
        out.append({**u, "enrolled_at": e["enrolled_at"], "completed": completed, "total": len(lesson_ids),
                    "percent": round(completed * 100 / len(lesson_ids)) if lesson_ids else 0})
    return ok(out)


def _enrolled_lesson(lesson_id):
    lesson = lesson_or_404(lesson_id)
    if not is_enrolled(g.user, lesson["course_id"]):
        raise ApiError("Anda belum terdaftar di kursus ini", 403)
    return lesson


@bp.post("/api/lessons/<int:lesson_id>/complete")
@auth_required("student")
def complete_lesson(lesson_id):
    lesson = _enrolled_lesson(lesson_id)
    existing = db.one(db.table("lesson_progress").select("id").eq("user_id", g.user["id"]).eq("lesson_id", lesson_id).limit(1).execute())
    if existing:
        status, message = 200, "Pelajaran sudah ditandai selesai"
    else:
        db.table("lesson_progress").insert({"user_id": g.user["id"], "lesson_id": lesson_id}).execute()
        status, message = 201, "Pelajaran ditandai selesai"
    return ok(course_progress(g.user["id"], lesson["course_id"]), message, status)


@bp.delete("/api/lessons/<int:lesson_id>/complete")
@auth_required("student")
def uncomplete_lesson(lesson_id):
    lesson = _enrolled_lesson(lesson_id)
    db.table("lesson_progress").delete().eq("user_id", g.user["id"]).eq("lesson_id", lesson_id).execute()
    return ok(course_progress(g.user["id"], lesson["course_id"]), "Tanda selesai dibatalkan")
