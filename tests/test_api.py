"""Pengujian end-to-end API memakai database tiruan. Jalankan: python -m unittest -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db  # noqa: E402
from tests.fake_supabase import FakeSupabase  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"JWT_SECRET": "x" * 40, "TESTING": True})
        self.fake = FakeSupabase()
        db._client = self.fake
        self.addCleanup(setattr, db, "_client", None)
        self.c = self.app.test_client()
        for name, email, role in (("Admin", "admin@t.test", "admin"), ("Guru", "guru@t.test", "instructor")):
            self.fake.table("users").insert(
                {"name": name, "email": email, "password_hash": generate_password_hash("Password123!"), "role": role}
            ).execute()
        self.admin = self.login("admin@t.test")
        self.teacher = self.login("guru@t.test")

    # helpers
    def req(self, method, path, token=None, body=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        r = getattr(self.c, method)(path, json=body, headers=headers)
        return r.status_code, r.get_json()

    def login(self, email, pw="Password123!"):
        return self.req("post", "/api/auth/login", body={"email": email, "password": pw})[1]["data"]["token"]

    def setup_course(self, publish=True):
        _, cat = self.req("post", "/api/categories", self.admin, {"name": "Pemrograman"})
        _, course = self.req("post", "/api/courses", self.teacher,
                             {"title": "Python Dasar", "category_id": cat["data"]["id"], "is_published": publish})
        return cat["data"], course["data"]

    # tests
    def test_health_and_root(self):
        self.assertEqual(self.req("get", "/api/health")[0], 200)
        self.assertEqual(self.req("get", "/api")[0], 200)
        self.assertEqual(self.c.get("/").status_code, 200)

    def test_unknown_endpoint_json(self):
        status, body = self.req("get", "/api/tidak-ada")
        self.assertEqual((status, "error" in body), (404, True))

    def test_register_login_me(self):
        s, b = self.req("post", "/api/auth/register", body={"name": "Budi", "email": "Budi@T.test", "password": "rahasia123"})
        self.assertEqual(s, 201)
        self.assertEqual(b["data"]["user"]["role"], "student")
        self.assertNotIn("password_hash", b["data"]["user"])
        self.assertEqual(self.req("post", "/api/auth/register", body={"name": "Budi", "email": "budi@t.test", "password": "rahasia123"})[0], 409)
        self.assertEqual(self.req("post", "/api/auth/register", body={"name": "B", "email": "bad", "password": "x"})[0], 400)
        self.assertEqual(self.req("post", "/api/auth/login", body={"email": "budi@t.test", "password": "salah-salah"})[0], 401)
        token = self.login("budi@t.test", "rahasia123")
        s, me = self.req("get", "/api/auth/me", token)
        self.assertEqual((s, me["data"]["email"]), (200, "budi@t.test"))
        self.assertEqual(self.req("get", "/api/auth/me")[0], 401)
        self.assertEqual(self.req("get", "/api/auth/me", "token.palsu.xyz")[0], 401)
        s, _ = self.req("patch", "/api/auth/me", token, {"current_password": "rahasia123", "new_password": "barubaru123"})
        self.assertEqual(s, 200)
        self.login("budi@t.test", "barubaru123")

    def test_categories_crud_and_permissions(self):
        s, b = self.req("post", "/api/categories", self.teacher, {"name": "X"})
        self.assertEqual(s, 403)
        s, b = self.req("post", "/api/categories", self.admin, {"name": "Desain", "description": "UI"})
        self.assertEqual(s, 201)
        cid = b["data"]["id"]
        self.assertEqual(self.req("post", "/api/categories", self.admin, {"name": "Desain"})[0], 409)
        self.assertEqual(self.req("post", "/api/categories", self.admin, {})[0], 400)
        self.assertEqual(self.req("put", f"/api/categories/{cid}", self.admin, {"name": "Desain Grafis"})[0], 200)
        self.assertEqual(self.req("get", f"/api/categories/{cid}")[1]["data"]["name"], "Desain Grafis")
        self.assertEqual(self.req("get", "/api/categories/999")[0], 404)
        self.assertEqual(len(self.req("get", "/api/categories")[1]["data"]), 1)
        self.assertEqual(self.req("delete", f"/api/categories/{cid}", self.admin)[0], 200)
        self.assertEqual(self.req("get", f"/api/categories/{cid}")[0], 404)

    def test_course_lifecycle_and_access(self):
        cat, course = self.setup_course()
        cid = course["id"]
        self.assertEqual(course["category_name"], "Pemrograman")
        self.assertEqual(self.req("post", "/api/courses", self.teacher, {"title": "ab", "category_id": cat["id"]})[0], 400)
        self.assertEqual(self.req("post", "/api/courses", self.teacher, {"title": "Valid", "category_id": 999})[0], 400)
        # kategori yang dipakai kursus tidak bisa dihapus (FK restrict)
        self.assertEqual(self.req("delete", f"/api/categories/{cat['id']}", self.admin)[0], 409)
        # list publik hanya kursus published
        self.req("post", "/api/courses", self.teacher, {"title": "Draft Rahasia", "category_id": cat["id"]})
        s, b = self.req("get", "/api/courses")
        self.assertEqual((s, b["meta"]["total"]), (200, 1))
        self.assertEqual(len(self.req("get", "/api/courses?q=python")[1]["data"]), 1)
        self.assertEqual(self.req("get", "/api/courses?scope=mine", self.teacher)[1]["meta"]["total"], 2)
        self.assertEqual(self.req("get", "/api/courses?scope=mine")[0], 401)
        # PUT wajib lengkap, PATCH sebagian
        self.assertEqual(self.req("put", f"/api/courses/{cid}", self.teacher, {"title": "Python Lanjut"})[0], 400)
        s, b = self.req("patch", f"/api/courses/{cid}", self.teacher, {"level": "advanced"})
        self.assertEqual((s, b["data"]["level"]), (200, "advanced"))
        s, b = self.req("put", f"/api/courses/{cid}", self.teacher, {"title": "Python Lanjut", "category_id": cat["id"], "is_published": True})
        self.assertEqual((s, b["data"]["title"]), (200, "Python Lanjut"))
        # guru lain tidak boleh mengubah
        self.fake.table("users").insert({"name": "Guru2", "email": "g2@t.test",
                                         "password_hash": generate_password_hash("Password123!"), "role": "instructor"}).execute()
        other = self.login("g2@t.test")
        self.assertEqual(self.req("patch", f"/api/courses/{cid}", other, {"level": "beginner"})[0], 403)
        self.assertEqual(self.req("delete", f"/api/courses/{cid}", other)[0], 403)
        self.assertEqual(self.req("get", "/api/courses/999")[0], 404)
        self.assertEqual(self.req("delete", f"/api/courses/{cid}", self.teacher)[0], 200)
        self.assertEqual(self.req("get", f"/api/courses/{cid}")[0], 404)

    def test_full_learning_flow(self):
        _, course = self.setup_course()
        cid = course["id"]
        s, l1 = self.req("post", f"/api/courses/{cid}/lessons", self.teacher, {"title": "Pelajaran 1", "content": "Isi"})
        self.assertEqual((s, l1["data"]["position"]), (201, 1))
        l2 = self.req("post", f"/api/courses/{cid}/lessons", self.teacher, {"title": "Pelajaran 2", "video_url": "https://youtu.be/abc"})[1]["data"]
        self.assertEqual(l2["position"], 2)
        self.assertEqual(self.req("post", f"/api/courses/{cid}/lessons", self.teacher, {"title": "Bad", "video_url": "javascript:alert(1)"})[0], 400)
        l1 = l1["data"]
        # siswa
        stu = self.req("post", "/api/auth/register", body={"name": "Budi", "email": "b@t.test", "password": "rahasia123"})[1]["data"]["token"]
        self.assertEqual(self.req("get", f"/api/lessons/{l1['id']}", stu)[0], 403)  # belum enroll
        self.assertEqual(self.req("post", f"/api/courses/{cid}/enroll", self.teacher)[0], 403)  # hanya siswa
        self.assertEqual(self.req("post", f"/api/courses/{cid}/enroll", stu)[0], 201)
        self.assertEqual(self.req("post", f"/api/courses/{cid}/enroll", stu)[0], 409)
        self.assertEqual(self.req("get", f"/api/lessons/{l1['id']}", stu)[1]["data"]["next_lesson_id"], l2["id"])
        s, b = self.req("post", f"/api/lessons/{l1['id']}/complete", stu)
        self.assertEqual((s, b["data"]["percent"]), (201, 50))
        self.assertEqual(self.req("post", f"/api/lessons/{l1['id']}/complete", stu)[0], 200)  # idempotent
        s, b = self.req("get", "/api/enrollments/me", stu)
        self.assertEqual(b["data"][0]["progress"], {"completed": 1, "total": 2, "percent": 50})
        detail = self.req("get", f"/api/courses/{cid}", stu)[1]["data"]
        self.assertTrue(detail["is_enrolled"])
        self.assertTrue(detail["lessons"][0]["is_completed"])
        self.assertEqual(self.req("get", f"/api/courses/{cid}/students", stu)[0], 403)
        s, b = self.req("get", f"/api/courses/{cid}/students", self.teacher)
        self.assertEqual((s, b["data"][0]["completed"]), (200, 1))
        self.assertEqual(self.req("delete", f"/api/lessons/{l1['id']}/complete", stu)[1]["data"]["percent"], 0)
        # edit & hapus pelajaran
        self.assertEqual(self.req("patch", f"/api/lessons/{l2['id']}", self.teacher, {"title": "Judul Baru"})[0], 200)
        self.assertEqual(self.req("put", f"/api/lessons/{l2['id']}", self.teacher, {"content": "x"})[0], 400)
        self.assertEqual(self.req("get", f"/api/courses/{cid}/lessons", stu)[0], 200)
        self.assertEqual(self.req("delete", f"/api/lessons/{l2['id']}", self.teacher)[0], 200)
        self.assertEqual(self.req("get", f"/api/lessons/{l2['id']}", self.teacher)[0], 404)
        # keluar kursus
        self.assertEqual(self.req("delete", f"/api/courses/{cid}/enroll", stu)[0], 200)
        self.assertEqual(self.req("delete", f"/api/courses/{cid}/enroll", stu)[0], 404)
        s, b = self.req("get", "/api/stats")
        self.assertEqual((s, b["data"]["courses"], b["data"]["students"]), (200, 1, 1))

    def test_user_management(self):
        stu = self.req("post", "/api/auth/register", body={"name": "Budi", "email": "b@t.test", "password": "rahasia123"})[1]["data"]
        sid = stu["user"]["id"]
        self.assertEqual(self.req("get", "/api/users", stu["token"])[0], 403)
        s, b = self.req("get", "/api/users", self.admin)
        self.assertEqual((s, b["meta"]["total"]), (200, 3))
        self.assertEqual(self.req("get", "/api/users?role=student", self.admin)[1]["meta"]["total"], 1)
        s, b = self.req("patch", f"/api/users/{sid}", self.admin, {"role": "instructor"})
        self.assertEqual((s, b["data"]["role"]), (200, "instructor"))
        self.assertEqual(self.req("patch", f"/api/users/{sid}", self.admin, {"role": "superuser"})[0], 400)
        admin_id = self.req("get", "/api/auth/me", self.admin)[1]["data"]["id"]
        self.assertEqual(self.req("patch", f"/api/users/{admin_id}", self.admin, {"role": "student"})[0], 400)
        self.assertEqual(self.req("delete", f"/api/users/{admin_id}", self.admin)[0], 400)
        self.assertEqual(self.req("get", f"/api/users/{sid}", self.admin)[0], 200)
        self.assertEqual(self.req("delete", f"/api/users/{sid}", self.admin)[0], 200)
        self.assertEqual(self.req("get", f"/api/users/{sid}", self.admin)[0], 404)

    def test_bad_json_and_headers(self):
        r = self.c.post("/api/auth/login", data="bukan json", content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"], "Body harus berupa JSON object")
        self.assertEqual(self.c.get("/api/health", headers={"Origin": "https://x.test"}).headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(self.c.get("/api").headers["X-Content-Type-Options"], "nosniff")


if __name__ == "__main__":
    unittest.main(verbosity=2)
