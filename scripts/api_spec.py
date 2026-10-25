"""Spesifikasi endpoint: satu sumber untuk README, docs/API.md, dan koleksi Postman."""

BASE = "https://nama-project.vercel.app"
TS = "2026-10-25T08:00:00+00:00"
USER = {"id": 4, "name": "Budi Siswa", "email": "budi@example.com", "role": "student", "created_at": TS}
CAT = {"id": 1, "name": "Pemrograman", "description": "Belajar menulis kode"}
COURSE = {"id": 1, "title": "Dasar Pemrograman Python", "description": "Mulai dari variabel hingga fungsi.",
          "category_id": 1, "instructor_id": 2, "level": "beginner", "is_published": True, "created_at": TS,
          "updated_at": TS, "category_name": "Pemrograman", "instructor_name": "Bu Sari Pengajar",
          "lesson_count": 3, "student_count": 1}
LESSON = {"id": 1, "course_id": 1, "title": "Mengenal Python dan Variabel", "content": "## Apa itu variabel?\n...",
          "video_url": None, "position": 1, "created_at": TS}
PROGRESS = {"completed": 1, "total": 3, "percent": 33}
TOKEN = "eyJhbGciOiJIUzI1NiIs..."
STUDENT, TEACHER, ADMIN = ("student",), ("instructor", "admin"), ("admin",)


def E(group, name, method, path, desc, auth=None, body=None, ok=(200, None), errors=(), roles=()):
    return dict(group=group, name=name, method=method, path=path, desc=desc, auth=auth, body=body, ok=ok,
                errors=list(errors), roles=roles)


def login_ok(msg, status=200):
    return (status, {"message": msg, "data": {"user": USER, "token": TOKEN}})


ENDPOINTS = [
    # ---------------- Umum ----------------
    E("Umum", "Health Check", "GET", "/api/health", "Memeriksa server dan koneksi database.",
      ok=(200, {"data": {"status": "ok", "database": "up"}}),
      errors=[(503, "{\"status\": \"error\", \"database\": \"down\"}")]),
    E("Umum", "Statistik Publik", "GET", "/api/stats", "Jumlah kursus terbit, pelajaran, dan siswa.",
      ok=(200, {"data": {"courses": 3, "lessons": 8, "students": 1}})),
    # ---------------- Auth ----------------
    E("Auth", "Register", "POST", "/api/auth/register", "Mendaftar akun baru (role otomatis student).",
      body={"name": "Budi Siswa", "email": "budi@example.com", "password": "rahasia123"},
      ok=login_ok("Registrasi berhasil", 201), errors=[(400, "Format email tidak valid"), (409, "Email sudah terdaftar")]),
    E("Auth", "Login", "POST", "/api/auth/login", "Login dan mendapatkan JWT (berlaku 24 jam).",
      body={"email": "student@lms.test", "password": "Password123!"}, ok=login_ok("Login berhasil"),
      errors=[(400, "Field password wajib diisi"), (401, "Email atau password salah")]),
    E("Auth", "Profil Saya", "GET", "/api/auth/me", "Data akun yang sedang login.", auth=True, ok=(200, {"data": USER})),
    E("Auth", "Ubah Profil", "PATCH", "/api/auth/me", "Ubah nama dan/atau password (wajib menyertakan current_password).",
      auth=True, body={"name": "Budi Santoso", "current_password": "rahasia123", "new_password": "passwordbaru123"},
      ok=(200, {"message": "Profil berhasil diperbarui", "data": USER}), errors=[(400, "Password saat ini salah")]),
    # ---------------- Kategori ----------------
    E("Kategori", "Daftar Kategori", "GET", "/api/categories", "Semua kategori (urut nama).", ok=(200, {"data": [CAT]})),
    E("Kategori", "Detail Kategori", "GET", "/api/categories/1", "Satu kategori berdasarkan ID.", ok=(200, {"data": CAT}),
      errors=[(404, "Kategori tidak ditemukan")]),
    E("Kategori", "Tambah Kategori", "POST", "/api/categories", "Menambah kategori baru. Khusus admin.", auth=True, roles=ADMIN,
      body={"name": "Pemrograman", "description": "Belajar menulis kode"},
      ok=(201, {"message": "Kategori berhasil ditambahkan", "data": CAT}),
      errors=[(400, "Field name wajib diisi"), (409, "Data sudah ada (duplikat)")]),
    E("Kategori", "Ubah Kategori", "PUT", "/api/categories/1", "Mengubah seluruh data kategori. Khusus admin.", auth=True, roles=ADMIN,
      body={"name": "Pemrograman Web", "description": "HTML, CSS, JS"},
      ok=(200, {"message": "Kategori berhasil diperbarui", "data": {**CAT, "name": "Pemrograman Web"}}),
      errors=[(404, "Kategori tidak ditemukan")]),
    E("Kategori", "Hapus Kategori", "DELETE", "/api/categories/1", "Menghapus kategori. Khusus admin; gagal jika masih dipakai kursus.",
      auth=True, roles=ADMIN, ok=(200, {"message": "Kategori berhasil dihapus"}),
      errors=[(409, "Data terhubung dengan data lain sehingga tidak dapat diproses")]),
    # ---------------- Kursus ----------------
    E("Kursus", "Daftar Kursus", "GET", "/api/courses?q=python&category_id=1&level=beginner&page=1&per_page=12",
      "Kursus terbit dengan pencarian judul (`q`), filter `category_id`, `level`, dan paginasi. "
      "Tambahkan `scope=mine` (instruktur/admin: kursus milik sendiri termasuk draf) atau `scope=all` (admin) dengan token.",
      ok=(200, {"data": [COURSE], "meta": {"page": 1, "per_page": 12, "total": 1}}),
      errors=[(400, "Field level harus salah satu dari: beginner, intermediate, advanced")]),
    E("Kursus", "Detail Kursus", "GET", "/api/courses/1",
      "Detail kursus + daftar pelajaran (tanpa isi materi). Token opsional; bila siswa terdaftar, muncul status selesai per pelajaran.",
      ok=(200, {"data": {**COURSE, "lessons": [{"id": 1, "title": "Mengenal Python dan Variabel", "position": 1}],
                         "is_enrolled": False, "can_manage": False}}),
      errors=[(404, "Kursus tidak ditemukan")]),
    E("Kursus", "Tambah Kursus", "POST", "/api/courses", "Membuat kursus. Instruktur/admin. Pemilik = user yang login.",
      auth=True, roles=TEACHER, body={"title": "Dasar Pemrograman Python", "description": "Mulai dari variabel hingga fungsi.",
                                      "category_id": 1, "level": "beginner", "is_published": True},
      ok=(201, {"message": "Kursus berhasil ditambahkan", "data": COURSE}),
      errors=[(400, "Field title wajib diisi"), (400, "Kategori tidak ditemukan")]),
    E("Kursus", "Ubah Kursus (PUT)", "PUT", "/api/courses/1", "Mengubah seluruh data kursus (title dan category_id wajib). Pemilik atau admin.",
      auth=True, roles=TEACHER, body={"title": "Python untuk Pemula", "description": "Versi revisi.", "category_id": 1,
                                      "level": "beginner", "is_published": True},
      ok=(200, {"message": "Kursus berhasil diperbarui", "data": {**COURSE, "title": "Python untuk Pemula"}}),
      errors=[(403, "Hanya pemilik kursus atau admin yang dapat melakukan aksi ini"), (404, "Kursus tidak ditemukan")]),
    E("Kursus", "Ubah Sebagian Kursus (PATCH)", "PATCH", "/api/courses/1", "Mengubah sebagian field kursus, mis. menerbitkan draf.",
      auth=True, roles=TEACHER, body={"is_published": True},
      ok=(200, {"message": "Kursus berhasil diperbarui", "data": COURSE}), errors=[(400, "Tidak ada field yang diubah")]),
    E("Kursus", "Hapus Kursus", "DELETE", "/api/courses/1", "Menghapus kursus beserta pelajaran dan pendaftarannya. Pemilik atau admin.",
      auth=True, roles=TEACHER, ok=(200, {"message": "Kursus berhasil dihapus"}),
      errors=[(403, "Hanya pemilik kursus atau admin yang dapat melakukan aksi ini"), (404, "Kursus tidak ditemukan")]),
    # ---------------- Pelajaran ----------------
    E("Pelajaran", "Daftar Pelajaran Kursus", "GET", "/api/courses/1/lessons", "Pelajaran lengkap dengan materi. Hanya siswa terdaftar, pemilik, atau admin.",
      auth=True, ok=(200, {"data": [LESSON]}), errors=[(403, "Anda belum terdaftar di kursus ini")]),
    E("Pelajaran", "Tambah Pelajaran", "POST", "/api/courses/1/lessons", "Menambah pelajaran. `position` otomatis di urutan akhir bila kosong.",
      auth=True, roles=TEACHER, body={"title": "Mengenal Python dan Variabel", "content": "## Apa itu variabel?\n...", "video_url": "https://youtu.be/rfscVS0vtbw"},
      ok=(201, {"message": "Pelajaran berhasil ditambahkan", "data": LESSON}),
      errors=[(400, "Field video_url harus berupa URL http/https yang valid")]),
    E("Pelajaran", "Detail Pelajaran", "GET", "/api/lessons/1", "Isi pelajaran + navigasi sebelumnya/berikutnya dan status selesai.",
      auth=True, ok=(200, {"data": {**LESSON, "course_title": "Dasar Pemrograman Python", "is_completed": False,
                                    "prev_lesson_id": None, "next_lesson_id": 2}}),
      errors=[(403, "Anda belum terdaftar di kursus ini"), (404, "Pelajaran tidak ditemukan")]),
    E("Pelajaran", "Ubah Pelajaran (PUT)", "PUT", "/api/lessons/1", "Mengubah seluruh data pelajaran (title wajib).",
      auth=True, roles=TEACHER, body={"title": "Variabel di Python", "content": "Materi baru", "video_url": "", "position": 1},
      ok=(200, {"message": "Pelajaran berhasil diperbarui", "data": {**LESSON, "title": "Variabel di Python"}}),
      errors=[(400, "Field title wajib diisi")]),
    E("Pelajaran", "Ubah Sebagian Pelajaran (PATCH)", "PATCH", "/api/lessons/1", "Mengubah sebagian field pelajaran, mis. urutan.",
      auth=True, roles=TEACHER, body={"position": 2},
      ok=(200, {"message": "Pelajaran berhasil diperbarui", "data": {**LESSON, "position": 2}}), errors=[(404, "Pelajaran tidak ditemukan")]),
    E("Pelajaran", "Hapus Pelajaran", "DELETE", "/api/lessons/1", "Menghapus pelajaran.", auth=True, roles=TEACHER,
      ok=(200, {"message": "Pelajaran berhasil dihapus"}), errors=[(404, "Pelajaran tidak ditemukan")]),
    # ---------------- Pembelajaran ----------------
    E("Pembelajaran", "Daftar ke Kursus", "POST", "/api/courses/1/enroll", "Siswa mendaftar ke kursus terbit.", auth=True, roles=STUDENT,
      ok=(201, {"message": "Berhasil mendaftar ke kursus", "data": {"id": 1, "user_id": 4, "course_id": 1, "enrolled_at": TS}}),
      errors=[(404, "Kursus tidak ditemukan"), (409, "Anda sudah terdaftar di kursus ini")]),
    E("Pembelajaran", "Keluar dari Kursus", "DELETE", "/api/courses/1/enroll", "Membatalkan pendaftaran (progres kursus ikut dihapus).",
      auth=True, roles=STUDENT, ok=(200, {"message": "Anda keluar dari kursus"}), errors=[(404, "Anda belum terdaftar di kursus ini")]),
    E("Pembelajaran", "Kursus Saya", "GET", "/api/enrollments/me", "Kursus yang diikuti beserta progresnya.", auth=True,
      ok=(200, {"data": [{**COURSE, "enrolled_at": TS, "progress": PROGRESS}]})),
    E("Pembelajaran", "Siswa Terdaftar", "GET", "/api/courses/1/students", "Daftar siswa dan progres di kursus. Pemilik atau admin.",
      auth=True, roles=TEACHER, ok=(200, {"data": [{"id": 4, "name": "Budi Siswa", "email": "budi@example.com", "enrolled_at": TS,
                                                    "completed": 1, "total": 3, "percent": 33}]}),
      errors=[(403, "Hanya pemilik kursus atau admin yang dapat melakukan aksi ini")]),
    E("Pembelajaran", "Tandai Pelajaran Selesai", "POST", "/api/lessons/1/complete", "Menandai selesai (idempotent: 201 pertama kali, 200 jika sudah).",
      auth=True, roles=STUDENT, ok=(201, {"message": "Pelajaran ditandai selesai", "data": PROGRESS}),
      errors=[(403, "Anda belum terdaftar di kursus ini")]),
    E("Pembelajaran", "Batalkan Tanda Selesai", "DELETE", "/api/lessons/1/complete", "Menghapus tanda selesai.", auth=True, roles=STUDENT,
      ok=(200, {"message": "Tanda selesai dibatalkan", "data": {"completed": 0, "total": 3, "percent": 0}}),
      errors=[(404, "Pelajaran tidak ditemukan")]),
    # ---------------- Pengguna ----------------
    E("Pengguna", "Daftar Pengguna", "GET", "/api/users?role=student&page=1&per_page=20", "Semua pengguna. Khusus admin.", auth=True, roles=ADMIN,
      ok=(200, {"data": [USER], "meta": {"page": 1, "per_page": 20, "total": 1}}),
      errors=[(400, "Field role harus salah satu dari: admin, instructor, student")]),
    E("Pengguna", "Detail Pengguna", "GET", "/api/users/4", "Satu pengguna. Khusus admin.", auth=True, roles=ADMIN,
      ok=(200, {"data": USER}), errors=[(404, "Pengguna tidak ditemukan")]),
    E("Pengguna", "Ubah Pengguna", "PATCH", "/api/users/4", "Mengubah nama/role pengguna. Khusus admin.", auth=True, roles=ADMIN,
      body={"role": "instructor"}, ok=(200, {"message": "Pengguna berhasil diperbarui", "data": {**USER, "role": "instructor"}}),
      errors=[(400, "Anda tidak dapat menurunkan role akun Anda sendiri")]),
    E("Pengguna", "Hapus Pengguna", "DELETE", "/api/users/4", "Menghapus pengguna. Khusus admin; gagal jika pengajar masih punya kursus.",
      auth=True, roles=ADMIN, ok=(200, {"message": "Pengguna berhasil dihapus"}),
      errors=[(400, "Anda tidak dapat menghapus akun Anda sendiri"), (409, "Data terhubung dengan data lain sehingga tidak dapat diproses")]),
]

for _e in ENDPOINTS:  # error umum untuk endpoint terproteksi
    if _e["auth"]:
        _e["errors"] = [(401, "Token autentikasi diperlukan")] + _e["errors"]
    if _e["roles"]:
        _e["errors"].insert(1, (403, "Anda tidak memiliki akses ke resource ini"))
