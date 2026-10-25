"""Aturan akses bersama: siapa boleh melihat / mengelola kursus dan pelajaran."""
from . import db
from .utils import ApiError


def course_or_404(course_id: int) -> dict:
    course = db.get_by_id("courses", course_id)
    if not course:
        raise ApiError("Kursus tidak ditemukan", 404)
    return course


def lesson_or_404(lesson_id: int) -> dict:
    lesson = db.get_by_id("lessons", lesson_id)
    if not lesson:
        raise ApiError("Pelajaran tidak ditemukan", 404)
    return lesson


def is_manager(user, course) -> bool:
    return bool(user) and (user["role"] == "admin" or course["instructor_id"] == user["id"])


def is_enrolled(user, course_id: int) -> bool:
    if not user:
        return False
    res = (
        db.table("enrollments").select("id").eq("user_id", user["id"]).eq("course_id", course_id).limit(1).execute()
    )
    return db.one(res) is not None


def require_manager(user, course):
    if not is_manager(user, course):
        raise ApiError("Hanya pemilik kursus atau admin yang dapat melakukan aksi ini", 403)


def require_access(user, course):
    if not (is_manager(user, course) or is_enrolled(user, course["id"])):
        raise ApiError("Anda belum terdaftar di kursus ini", 403)


def course_progress(user_id: int, course_id: int) -> dict:
    lessons = db.table("lessons").select("id").eq("course_id", course_id).execute().data
    ids = {r["id"] for r in lessons}
    done = db.table("lesson_progress").select("lesson_id").eq("user_id", user_id).execute().data
    completed = len(ids & {r["lesson_id"] for r in done})
    total = len(ids)
    return {"completed": completed, "total": total, "percent": round(completed * 100 / total) if total else 0}
