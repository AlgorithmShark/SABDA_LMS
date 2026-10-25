# SABDA LMS - REST API Learning Management System

Tugas Akhir Learning Labs: Backend Development.
REST API untuk sistem manajemen pembelajaran sederhana, lengkap dengan frontend web yang disajikan langsung oleh Flask.

| Komponen | Teknologi |
|----------|-----------|
| Bahasa & Framework | Python 3.12, Flask 3 |
| Database | Supabase (PostgreSQL) |
| Autentikasi | JWT (PyJWT) + hash password scrypt (Werkzeug) |
| Frontend | HTML, CSS, JavaScript murni (single page app, tanpa build step) |
| Deployment | Vercel (Python serverless function) |

## 1. Deskripsi Project

SABDA mempertemukan tiga jenis pengguna:

- **Student** mendaftar ke kursus, membaca pelajaran, menandai pelajaran selesai, dan melihat progres belajar.
- **Instructor** membuat kursus dan pelajaran, menerbitkan kursus, serta memantau progres siswanya.
- **Admin** mengelola kategori dan pengguna (mengubah role, menghapus akun), dan dapat mengelola semua kursus.

Registrasi publik selalu membuat akun `student`. Role `instructor` dan `admin` hanya bisa diberikan oleh admin.

## 2. Link Deployment

- **Aplikasi (frontend + API)** : `https://nama-project.vercel.app` (ganti dengan URL Vercel Anda)
- **Repository GitHub** : `https://github.com/username/nama-repo` (ganti dengan repo Anda)

> Semua contoh URL pada dokumentasi memakai `https://nama-project.vercel.app`. Ganti dengan URL deployment Anda.

## 3. ERD / Skema Database

6 tabel yang saling terhubung lewat foreign key. File sumber: [`database/schema.sql`](database/schema.sql), diagram: [`docs/erd.png`](docs/erd.png) (vektor: [`erd.svg`](docs/erd.svg), versi dbdiagram.io: [`database/erd.dbml`](database/erd.dbml)).

![ERD SABDA LMS](docs/erd.png)

| Tabel | Primary Key | Foreign Key | Relasi |
|-------|-------------|-------------|--------|
| `users` | `id` | - | Satu user (instructor) punya banyak `courses` |
| `categories` | `id` | - | Satu kategori punya banyak `courses` (one-to-many) |
| `courses` | `id` | `category_id`, `instructor_id` | Satu course punya banyak `lessons` |
| `lessons` | `id` | `course_id` | Dihapus otomatis saat course dihapus (cascade) |
| `enrollments` | `id` | `user_id`, `course_id` | **Pivot many-to-many** `users` dan `courses` |
| `lesson_progress` | `id` | `user_id`, `lesson_id` | **Pivot many-to-many** `users` dan `lessons` |

Aturan integritas: `unique(user_id, course_id)` dan `unique(user_id, lesson_id)` mencegah data ganda. Kategori dan pengajar yang masih dipakai kursus tidak bisa dihapus (`on delete restrict`), sedangkan pelajaran dan pendaftaran ikut terhapus bersama kursusnya (`on delete cascade`). View `course_stats` menghitung jumlah pelajaran dan siswa per kursus.

## 4. Struktur Folder

```
SABDA-lms/
├── api/index.py             # entry point Vercel
├── app/
│   ├── __init__.py          # app factory, error handler, CORS & security headers
│   ├── config.py, db.py     # konfigurasi env & koneksi Supabase
│   ├── utils.py, access.py  # validasi, JWT, aturan akses
│   ├── routes/              # auth, categories, courses(+lessons), learning, users
│   ├── templates/index.html # frontend
│   └── static/              # css/style.css, js/app.js
├── database/                # schema.sql, seed.sql, erd.dbml
├── docs/                    # erd.png, erd.svg, API.md
├── postman/                 # koleksi Postman / Thunder Client
├── scripts/                 # generator dokumentasi
├── tests/                   # tes otomatis (database tiruan)
├── vercel.json, requirements.txt, .env.example, run.py
```

## 5. Menjalankan Secara Lokal

Prasyarat: Python 3.10+ dan akun Supabase (gratis).

### 5.1 Siapkan database Supabase

1. Buka [supabase.com](https://supabase.com), buat **New project**, dan catat password database Anda.
2. Buka **SQL Editor > New query**, tempel seluruh isi [`database/schema.sql`](database/schema.sql), lalu klik **Run**.
3. *(Opsional, untuk demo)* jalankan [`database/seed.sql`](database/seed.sql) dengan cara yang sama. Isinya 3 kategori, 4 kursus, 8 pelajaran, dan 3 akun demo.
4. Buka **Project Settings > API** dan salin:
   - **Project URL** menjadi `SUPABASE_URL`
   - **service_role key** menjadi `SUPABASE_SERVICE_ROLE_KEY` (tab *Legacy API keys*, berawalan `eyJ...`). Key ini rahasia, jangan pernah dimasukkan ke kode atau frontend.

### 5.2 Jalankan aplikasi

```bash
git clone https://github.com/username/nama-repo.git && cd nama-repo
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # Windows: copy .env.example .env
# isi SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, dan JWT_SECRET di file .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # contoh pembuat JWT_SECRET

python run.py
```

Buka `http://127.0.0.1:5000` untuk frontend dan `http://127.0.0.1:5000/api/health` untuk cek koneksi database (harus `{"data": {"status": "ok", "database": "up"}}`).

### 5.3 Akun demo (hanya jika `seed.sql` dijalankan)

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@lms.test` | `Password123!` |
| Instructor | `instructor@lms.test` | `Password123!` |
| Student | `student@lms.test` | `Password123!` |

> **Sebelum dipakai sungguhan:** hapus akun demo atau ganti passwordnya. Untuk membuat admin sendiri, daftar lewat aplikasi, lalu di Supabase SQL Editor jalankan `update users set role = 'admin' where email = 'email-anda@contoh.com';`

### 5.4 Menjalankan tes otomatis

```bash
python -m unittest discover -s tests -t . -v
```

Tes memakai database tiruan di memori sehingga tidak membutuhkan Supabase.

## 6. Deploy ke Vercel

Konfigurasi sudah disiapkan di [`vercel.json`](vercel.json) dan [`api/index.py`](api/index.py).

### Cara A: lewat GitHub (disarankan)

1. Push proyek ke GitHub. Pastikan `.env` **tidak** ikut ter-commit (sudah ada di `.gitignore`).
2. Di [vercel.com/new](https://vercel.com/new), **Import** repository tersebut. Framework Preset biarkan **Other**.
3. Sebelum klik **Deploy**, buka **Environment Variables** dan isi:

   | Nama | Nilai |
   |------|-------|
   | `SUPABASE_URL` | Project URL Supabase |
   | `SUPABASE_SERVICE_ROLE_KEY` | service_role key |
   | `JWT_SECRET` | string acak minimal 32 karakter |
   | `JWT_EXPIRES_HOURS` | `24` (opsional) |
   | `CORS_ORIGINS` | `*` atau daftar origin dipisah koma (opsional) |

4. Klik **Deploy**. Setelah selesai, buka `https://nama-project.vercel.app/api/health`.

### Cara B: lewat Vercel CLI

```bash
npm i -g vercel
vercel login
vercel link
vercel env add SUPABASE_URL production
vercel env add SUPABASE_SERVICE_ROLE_KEY production
vercel env add JWT_SECRET production
vercel --prod
```

Setiap kali kode berubah dan di-push ke branch utama, Vercel otomatis melakukan deploy ulang. Jika Anda mengubah environment variable, lakukan **Redeploy** agar nilainya terpakai.

## 7. Pengujian dengan Postman / Thunder Client

1. Import [`postman/SABDA-LMS.postman_collection.json`](postman/SABDA-LMS.postman_collection.json) ke Postman, atau ke Thunder Client lewat *Collections > menu > Import*.
2. Ubah variabel collection `base_url` menjadi URL Vercel Anda (bukan `localhost`).
3. Jalankan **Auth > Login**. Token tersimpan otomatis di variabel `token` dan dipakai oleh semua request lain.
4. Pengujian per role: login sebagai admin untuk endpoint Kategori/Pengguna, sebagai instructor untuk Kursus/Pelajaran, dan sebagai student untuk Pembelajaran. Jalankan Login ulang setiap berpindah role.
5. Ambil screenshot request dan response untuk tiap endpoint, atau ekspor collection yang sudah berisi hasil sebagai bukti pengujian.

Contoh cepat dengan curl:

```bash
curl https://nama-project.vercel.app/api/courses
curl -X POST https://nama-project.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@lms.test","password":"Password123!"}'
```

## 8. Konvensi API

- Semua request dan response memakai **JSON**. Prefix semua endpoint: `/api`.
- Autentikasi: header `Authorization: Bearer <token>` (token didapat dari Login/Register).
- Response sukses: `{"message": "...", "data": ...}` dan untuk daftar berpaginasi ditambah `"meta": {"page", "per_page", "total"}`.
- Response error selalu: `{"error": "pesan yang jelas"}`.

| Status | Arti |
|--------|------|
| `200` OK / `201` Created | Berhasil (201 untuk data baru) |
| `400` | Input tidak valid atau field wajib kosong |
| `401` | Token tidak ada, tidak valid, atau kedaluwarsa |
| `403` | Role tidak berhak atau bukan pemilik data |
| `404` | Data / endpoint tidak ditemukan |
| `409` | Konflik: data duplikat atau masih terhubung dengan data lain |
| `500` / `503` | Kesalahan server / database tidak dapat dijangkau |

Resource dengan **CRUD lengkap**: `categories`, `courses`, dan `lessons`. Resource `users` mendukung Read, Update (PATCH), dan Delete oleh admin; pembuatan akun lewat Register. Endpoint `PUT` mengganti seluruh data, `PATCH` mengubah sebagian.

## 9. Dokumentasi Endpoint

33 endpoint. Versi mandiri ada di [`docs/API.md`](docs/API.md). Bagian ini dibuat otomatis dari `scripts/api_spec.py`.

<!-- API-DOCS:START -->

### Umum

#### 1. Health Check

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/health`
- **Deskripsi** : Memeriksa server dan koneksi database.
- **Akses** : Publik
- **Headers** : -
- **Response Sukses (200)** :

```json
{
  "data": {
    "status": "ok",
    "database": "up"
  }
}
```

- **Response Error (503)** : `{"status": "error", "database": "down"}`

#### 2. Statistik Publik

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/stats`
- **Deskripsi** : Jumlah kursus terbit, pelajaran, dan siswa.
- **Akses** : Publik
- **Headers** : -
- **Response Sukses (200)** :

```json
{
  "data": {
    "courses": 3,
    "lessons": 8,
    "students": 1
  }
}
```


### Auth

#### 3. Register

- **Method** : `POST`
- **URL** : `https://nama-project.vercel.app/api/auth/register`
- **Deskripsi** : Mendaftar akun baru (role otomatis student).
- **Akses** : Publik
- **Headers** : `Content-Type: application/json`
- **Request Body** :

```json
{
  "name": "Budi Siswa",
  "email": "budi@example.com",
  "password": "rahasia123"
}
```

- **Response Sukses (201)** :

```json
{
  "message": "Registrasi berhasil",
  "data": {
    "user": {
      "id": 4,
      "name": "Budi Siswa",
      "email": "budi@example.com",
      "role": "student",
      "created_at": "2026-10-25T08:00:00+00:00"
    },
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

- **Response Error (400)** : `{"error": "Format email tidak valid"}`
- **Response Error (409)** : `{"error": "Email sudah terdaftar"}`

#### 4. Login

- **Method** : `POST`
- **URL** : `https://nama-project.vercel.app/api/auth/login`
- **Deskripsi** : Login dan mendapatkan JWT (berlaku 24 jam).
- **Akses** : Publik
- **Headers** : `Content-Type: application/json`
- **Request Body** :

```json
{
  "email": "student@lms.test",
  "password": "Password123!"
}
```

- **Response Sukses (200)** :

```json
{
  "message": "Login berhasil",
  "data": {
    "user": {
      "id": 4,
      "name": "Budi Siswa",
      "email": "budi@example.com",
      "role": "student",
      "created_at": "2026-10-25T08:00:00+00:00"
    },
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

- **Response Error (400)** : `{"error": "Field password wajib diisi"}`
- **Response Error (401)** : `{"error": "Email atau password salah"}`

#### 5. Profil Saya

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/auth/me`
- **Deskripsi** : Data akun yang sedang login.
- **Akses** : Login (semua role)
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "data": {
    "id": 4,
    "name": "Budi Siswa",
    "email": "budi@example.com",
    "role": "student",
    "created_at": "2026-10-25T08:00:00+00:00"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`

#### 6. Ubah Profil

- **Method** : `PATCH`
- **URL** : `https://nama-project.vercel.app/api/auth/me`
- **Deskripsi** : Ubah nama dan/atau password (wajib menyertakan current_password).
- **Akses** : Login (semua role)
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "name": "Budi Santoso",
  "current_password": "rahasia123",
  "new_password": "passwordbaru123"
}
```

- **Response Sukses (200)** :

```json
{
  "message": "Profil berhasil diperbarui",
  "data": {
    "id": 4,
    "name": "Budi Siswa",
    "email": "budi@example.com",
    "role": "student",
    "created_at": "2026-10-25T08:00:00+00:00"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (400)** : `{"error": "Password saat ini salah"}`

### Kategori

#### 7. Daftar Kategori

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/categories`
- **Deskripsi** : Semua kategori (urut nama).
- **Akses** : Publik
- **Headers** : -
- **Response Sukses (200)** :

```json
{
  "data": [
    {
      "id": 1,
      "name": "Pemrograman",
      "description": "Belajar menulis kode"
    }
  ]
}
```


#### 8. Detail Kategori

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/categories/1`
- **Deskripsi** : Satu kategori berdasarkan ID.
- **Akses** : Publik
- **Headers** : -
- **Response Sukses (200)** :

```json
{
  "data": {
    "id": 1,
    "name": "Pemrograman",
    "description": "Belajar menulis kode"
  }
}
```

- **Response Error (404)** : `{"error": "Kategori tidak ditemukan"}`

#### 9. Tambah Kategori

- **Method** : `POST`
- **URL** : `https://nama-project.vercel.app/api/categories`
- **Deskripsi** : Menambah kategori baru. Khusus admin.
- **Akses** : Role: admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "name": "Pemrograman",
  "description": "Belajar menulis kode"
}
```

- **Response Sukses (201)** :

```json
{
  "message": "Kategori berhasil ditambahkan",
  "data": {
    "id": 1,
    "name": "Pemrograman",
    "description": "Belajar menulis kode"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (400)** : `{"error": "Field name wajib diisi"}`
- **Response Error (409)** : `{"error": "Data sudah ada (duplikat)"}`

#### 10. Ubah Kategori

- **Method** : `PUT`
- **URL** : `https://nama-project.vercel.app/api/categories/1`
- **Deskripsi** : Mengubah seluruh data kategori. Khusus admin.
- **Akses** : Role: admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "name": "Pemrograman Web",
  "description": "HTML, CSS, JS"
}
```

- **Response Sukses (200)** :

```json
{
  "message": "Kategori berhasil diperbarui",
  "data": {
    "id": 1,
    "name": "Pemrograman Web",
    "description": "Belajar menulis kode"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (404)** : `{"error": "Kategori tidak ditemukan"}`

#### 11. Hapus Kategori

- **Method** : `DELETE`
- **URL** : `https://nama-project.vercel.app/api/categories/1`
- **Deskripsi** : Menghapus kategori. Khusus admin; gagal jika masih dipakai kursus.
- **Akses** : Role: admin
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "message": "Kategori berhasil dihapus"
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (409)** : `{"error": "Data terhubung dengan data lain sehingga tidak dapat diproses"}`

### Kursus

#### 12. Daftar Kursus

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/courses?q=python&category_id=1&level=beginner&page=1&per_page=12`
- **Deskripsi** : Kursus terbit dengan pencarian judul (`q`), filter `category_id`, `level`, dan paginasi. Tambahkan `scope=mine` (instruktur/admin: kursus milik sendiri termasuk draf) atau `scope=all` (admin) dengan token.
- **Akses** : Publik
- **Headers** : -
- **Response Sukses (200)** :

```json
{
  "data": [
    {
      "id": 1,
      "title": "Dasar Pemrograman Python",
      "description": "Mulai dari variabel hingga fungsi.",
      "category_id": 1,
      "instructor_id": 2,
      "level": "beginner",
      "is_published": true,
      "created_at": "2026-10-25T08:00:00+00:00",
      "updated_at": "2026-10-25T08:00:00+00:00",
      "category_name": "Pemrograman",
      "instructor_name": "Bu Sari Pengajar",
      "lesson_count": 3,
      "student_count": 1
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 12,
    "total": 1
  }
}
```

- **Response Error (400)** : `{"error": "Field level harus salah satu dari: beginner, intermediate, advanced"}`

#### 13. Detail Kursus

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/courses/1`
- **Deskripsi** : Detail kursus + daftar pelajaran (tanpa isi materi). Token opsional; bila siswa terdaftar, muncul status selesai per pelajaran.
- **Akses** : Publik
- **Headers** : -
- **Response Sukses (200)** :

```json
{
  "data": {
    "id": 1,
    "title": "Dasar Pemrograman Python",
    "description": "Mulai dari variabel hingga fungsi.",
    "category_id": 1,
    "instructor_id": 2,
    "level": "beginner",
    "is_published": true,
    "created_at": "2026-10-25T08:00:00+00:00",
    "updated_at": "2026-10-25T08:00:00+00:00",
    "category_name": "Pemrograman",
    "instructor_name": "Bu Sari Pengajar",
    "lesson_count": 3,
    "student_count": 1,
    "lessons": [
      {
        "id": 1,
        "title": "Mengenal Python dan Variabel",
        "position": 1
      }
    ],
    "is_enrolled": false,
    "can_manage": false
  }
}
```

- **Response Error (404)** : `{"error": "Kursus tidak ditemukan"}`

#### 14. Tambah Kursus

- **Method** : `POST`
- **URL** : `https://nama-project.vercel.app/api/courses`
- **Deskripsi** : Membuat kursus. Instruktur/admin. Pemilik = user yang login.
- **Akses** : Role: instructor, admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "title": "Dasar Pemrograman Python",
  "description": "Mulai dari variabel hingga fungsi.",
  "category_id": 1,
  "level": "beginner",
  "is_published": true
}
```

- **Response Sukses (201)** :

```json
{
  "message": "Kursus berhasil ditambahkan",
  "data": {
    "id": 1,
    "title": "Dasar Pemrograman Python",
    "description": "Mulai dari variabel hingga fungsi.",
    "category_id": 1,
    "instructor_id": 2,
    "level": "beginner",
    "is_published": true,
    "created_at": "2026-10-25T08:00:00+00:00",
    "updated_at": "2026-10-25T08:00:00+00:00",
    "category_name": "Pemrograman",
    "instructor_name": "Bu Sari Pengajar",
    "lesson_count": 3,
    "student_count": 1
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (400)** : `{"error": "Field title wajib diisi"}`
- **Response Error (400)** : `{"error": "Kategori tidak ditemukan"}`

#### 15. Ubah Kursus (PUT)

- **Method** : `PUT`
- **URL** : `https://nama-project.vercel.app/api/courses/1`
- **Deskripsi** : Mengubah seluruh data kursus (title dan category_id wajib). Pemilik atau admin.
- **Akses** : Role: instructor, admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "title": "Python untuk Pemula",
  "description": "Versi revisi.",
  "category_id": 1,
  "level": "beginner",
  "is_published": true
}
```

- **Response Sukses (200)** :

```json
{
  "message": "Kursus berhasil diperbarui",
  "data": {
    "id": 1,
    "title": "Python untuk Pemula",
    "description": "Mulai dari variabel hingga fungsi.",
    "category_id": 1,
    "instructor_id": 2,
    "level": "beginner",
    "is_published": true,
    "created_at": "2026-10-25T08:00:00+00:00",
    "updated_at": "2026-10-25T08:00:00+00:00",
    "category_name": "Pemrograman",
    "instructor_name": "Bu Sari Pengajar",
    "lesson_count": 3,
    "student_count": 1
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (403)** : `{"error": "Hanya pemilik kursus atau admin yang dapat melakukan aksi ini"}`
- **Response Error (404)** : `{"error": "Kursus tidak ditemukan"}`

#### 16. Ubah Sebagian Kursus (PATCH)

- **Method** : `PATCH`
- **URL** : `https://nama-project.vercel.app/api/courses/1`
- **Deskripsi** : Mengubah sebagian field kursus, mis. menerbitkan draf.
- **Akses** : Role: instructor, admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "is_published": true
}
```

- **Response Sukses (200)** :

```json
{
  "message": "Kursus berhasil diperbarui",
  "data": {
    "id": 1,
    "title": "Dasar Pemrograman Python",
    "description": "Mulai dari variabel hingga fungsi.",
    "category_id": 1,
    "instructor_id": 2,
    "level": "beginner",
    "is_published": true,
    "created_at": "2026-10-25T08:00:00+00:00",
    "updated_at": "2026-10-25T08:00:00+00:00",
    "category_name": "Pemrograman",
    "instructor_name": "Bu Sari Pengajar",
    "lesson_count": 3,
    "student_count": 1
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (400)** : `{"error": "Tidak ada field yang diubah"}`

#### 17. Hapus Kursus

- **Method** : `DELETE`
- **URL** : `https://nama-project.vercel.app/api/courses/1`
- **Deskripsi** : Menghapus kursus beserta pelajaran dan pendaftarannya. Pemilik atau admin.
- **Akses** : Role: instructor, admin
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "message": "Kursus berhasil dihapus"
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (403)** : `{"error": "Hanya pemilik kursus atau admin yang dapat melakukan aksi ini"}`
- **Response Error (404)** : `{"error": "Kursus tidak ditemukan"}`

### Pelajaran

#### 18. Daftar Pelajaran Kursus

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/courses/1/lessons`
- **Deskripsi** : Pelajaran lengkap dengan materi. Hanya siswa terdaftar, pemilik, atau admin.
- **Akses** : Login (semua role)
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "data": [
    {
      "id": 1,
      "course_id": 1,
      "title": "Mengenal Python dan Variabel",
      "content": "## Apa itu variabel?\n...",
      "video_url": null,
      "position": 1,
      "created_at": "2026-10-25T08:00:00+00:00"
    }
  ]
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda belum terdaftar di kursus ini"}`

#### 19. Tambah Pelajaran

- **Method** : `POST`
- **URL** : `https://nama-project.vercel.app/api/courses/1/lessons`
- **Deskripsi** : Menambah pelajaran. `position` otomatis di urutan akhir bila kosong.
- **Akses** : Role: instructor, admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "title": "Mengenal Python dan Variabel",
  "content": "## Apa itu variabel?\n...",
  "video_url": "https://youtu.be/rfscVS0vtbw"
}
```

- **Response Sukses (201)** :

```json
{
  "message": "Pelajaran berhasil ditambahkan",
  "data": {
    "id": 1,
    "course_id": 1,
    "title": "Mengenal Python dan Variabel",
    "content": "## Apa itu variabel?\n...",
    "video_url": null,
    "position": 1,
    "created_at": "2026-10-25T08:00:00+00:00"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (400)** : `{"error": "Field video_url harus berupa URL http/https yang valid"}`

#### 20. Detail Pelajaran

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/lessons/1`
- **Deskripsi** : Isi pelajaran + navigasi sebelumnya/berikutnya dan status selesai.
- **Akses** : Login (semua role)
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "data": {
    "id": 1,
    "course_id": 1,
    "title": "Mengenal Python dan Variabel",
    "content": "## Apa itu variabel?\n...",
    "video_url": null,
    "position": 1,
    "created_at": "2026-10-25T08:00:00+00:00",
    "course_title": "Dasar Pemrograman Python",
    "is_completed": false,
    "prev_lesson_id": null,
    "next_lesson_id": 2
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda belum terdaftar di kursus ini"}`
- **Response Error (404)** : `{"error": "Pelajaran tidak ditemukan"}`

#### 21. Ubah Pelajaran (PUT)

- **Method** : `PUT`
- **URL** : `https://nama-project.vercel.app/api/lessons/1`
- **Deskripsi** : Mengubah seluruh data pelajaran (title wajib).
- **Akses** : Role: instructor, admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "title": "Variabel di Python",
  "content": "Materi baru",
  "video_url": "",
  "position": 1
}
```

- **Response Sukses (200)** :

```json
{
  "message": "Pelajaran berhasil diperbarui",
  "data": {
    "id": 1,
    "course_id": 1,
    "title": "Variabel di Python",
    "content": "## Apa itu variabel?\n...",
    "video_url": null,
    "position": 1,
    "created_at": "2026-10-25T08:00:00+00:00"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (400)** : `{"error": "Field title wajib diisi"}`

#### 22. Ubah Sebagian Pelajaran (PATCH)

- **Method** : `PATCH`
- **URL** : `https://nama-project.vercel.app/api/lessons/1`
- **Deskripsi** : Mengubah sebagian field pelajaran, mis. urutan.
- **Akses** : Role: instructor, admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "position": 2
}
```

- **Response Sukses (200)** :

```json
{
  "message": "Pelajaran berhasil diperbarui",
  "data": {
    "id": 1,
    "course_id": 1,
    "title": "Mengenal Python dan Variabel",
    "content": "## Apa itu variabel?\n...",
    "video_url": null,
    "position": 2,
    "created_at": "2026-10-25T08:00:00+00:00"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (404)** : `{"error": "Pelajaran tidak ditemukan"}`

#### 23. Hapus Pelajaran

- **Method** : `DELETE`
- **URL** : `https://nama-project.vercel.app/api/lessons/1`
- **Deskripsi** : Menghapus pelajaran.
- **Akses** : Role: instructor, admin
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "message": "Pelajaran berhasil dihapus"
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (404)** : `{"error": "Pelajaran tidak ditemukan"}`

### Pembelajaran

#### 24. Daftar ke Kursus

- **Method** : `POST`
- **URL** : `https://nama-project.vercel.app/api/courses/1/enroll`
- **Deskripsi** : Siswa mendaftar ke kursus terbit.
- **Akses** : Role: student
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (201)** :

```json
{
  "message": "Berhasil mendaftar ke kursus",
  "data": {
    "id": 1,
    "user_id": 4,
    "course_id": 1,
    "enrolled_at": "2026-10-25T08:00:00+00:00"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (404)** : `{"error": "Kursus tidak ditemukan"}`
- **Response Error (409)** : `{"error": "Anda sudah terdaftar di kursus ini"}`

#### 25. Keluar dari Kursus

- **Method** : `DELETE`
- **URL** : `https://nama-project.vercel.app/api/courses/1/enroll`
- **Deskripsi** : Membatalkan pendaftaran (progres kursus ikut dihapus).
- **Akses** : Role: student
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "message": "Anda keluar dari kursus"
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (404)** : `{"error": "Anda belum terdaftar di kursus ini"}`

#### 26. Kursus Saya

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/enrollments/me`
- **Deskripsi** : Kursus yang diikuti beserta progresnya.
- **Akses** : Login (semua role)
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "data": [
    {
      "id": 1,
      "title": "Dasar Pemrograman Python",
      "description": "Mulai dari variabel hingga fungsi.",
      "category_id": 1,
      "instructor_id": 2,
      "level": "beginner",
      "is_published": true,
      "created_at": "2026-10-25T08:00:00+00:00",
      "updated_at": "2026-10-25T08:00:00+00:00",
      "category_name": "Pemrograman",
      "instructor_name": "Bu Sari Pengajar",
      "lesson_count": 3,
      "student_count": 1,
      "enrolled_at": "2026-10-25T08:00:00+00:00",
      "progress": {
        "completed": 1,
        "total": 3,
        "percent": 33
      }
    }
  ]
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`

#### 27. Siswa Terdaftar

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/courses/1/students`
- **Deskripsi** : Daftar siswa dan progres di kursus. Pemilik atau admin.
- **Akses** : Role: instructor, admin
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "data": [
    {
      "id": 4,
      "name": "Budi Siswa",
      "email": "budi@example.com",
      "enrolled_at": "2026-10-25T08:00:00+00:00",
      "completed": 1,
      "total": 3,
      "percent": 33
    }
  ]
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (403)** : `{"error": "Hanya pemilik kursus atau admin yang dapat melakukan aksi ini"}`

#### 28. Tandai Pelajaran Selesai

- **Method** : `POST`
- **URL** : `https://nama-project.vercel.app/api/lessons/1/complete`
- **Deskripsi** : Menandai selesai (idempotent: 201 pertama kali, 200 jika sudah).
- **Akses** : Role: student
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (201)** :

```json
{
  "message": "Pelajaran ditandai selesai",
  "data": {
    "completed": 1,
    "total": 3,
    "percent": 33
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (403)** : `{"error": "Anda belum terdaftar di kursus ini"}`

#### 29. Batalkan Tanda Selesai

- **Method** : `DELETE`
- **URL** : `https://nama-project.vercel.app/api/lessons/1/complete`
- **Deskripsi** : Menghapus tanda selesai.
- **Akses** : Role: student
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "message": "Tanda selesai dibatalkan",
  "data": {
    "completed": 0,
    "total": 3,
    "percent": 0
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (404)** : `{"error": "Pelajaran tidak ditemukan"}`

### Pengguna

#### 30. Daftar Pengguna

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/users?role=student&page=1&per_page=20`
- **Deskripsi** : Semua pengguna. Khusus admin.
- **Akses** : Role: admin
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "data": [
    {
      "id": 4,
      "name": "Budi Siswa",
      "email": "budi@example.com",
      "role": "student",
      "created_at": "2026-10-25T08:00:00+00:00"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 1
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (400)** : `{"error": "Field role harus salah satu dari: admin, instructor, student"}`

#### 31. Detail Pengguna

- **Method** : `GET`
- **URL** : `https://nama-project.vercel.app/api/users/4`
- **Deskripsi** : Satu pengguna. Khusus admin.
- **Akses** : Role: admin
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "data": {
    "id": 4,
    "name": "Budi Siswa",
    "email": "budi@example.com",
    "role": "student",
    "created_at": "2026-10-25T08:00:00+00:00"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (404)** : `{"error": "Pengguna tidak ditemukan"}`

#### 32. Ubah Pengguna

- **Method** : `PATCH`
- **URL** : `https://nama-project.vercel.app/api/users/4`
- **Deskripsi** : Mengubah nama/role pengguna. Khusus admin.
- **Akses** : Role: admin
- **Headers** : `Content-Type: application/json` | `Authorization: Bearer <token>`
- **Request Body** :

```json
{
  "role": "instructor"
}
```

- **Response Sukses (200)** :

```json
{
  "message": "Pengguna berhasil diperbarui",
  "data": {
    "id": 4,
    "name": "Budi Siswa",
    "email": "budi@example.com",
    "role": "instructor",
    "created_at": "2026-10-25T08:00:00+00:00"
  }
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (400)** : `{"error": "Anda tidak dapat menurunkan role akun Anda sendiri"}`

#### 33. Hapus Pengguna

- **Method** : `DELETE`
- **URL** : `https://nama-project.vercel.app/api/users/4`
- **Deskripsi** : Menghapus pengguna. Khusus admin; gagal jika pengajar masih punya kursus.
- **Akses** : Role: admin
- **Headers** : `Authorization: Bearer <token>`
- **Response Sukses (200)** :

```json
{
  "message": "Pengguna berhasil dihapus"
}
```

- **Response Error (401)** : `{"error": "Token autentikasi diperlukan"}`
- **Response Error (403)** : `{"error": "Anda tidak memiliki akses ke resource ini"}`
- **Response Error (400)** : `{"error": "Anda tidak dapat menghapus akun Anda sendiri"}`
- **Response Error (409)** : `{"error": "Data terhubung dengan data lain sehingga tidak dapat diproses"}`

<!-- API-DOCS:END -->

## 10. Keamanan dan Kesiapan Production

- **Tidak ada secret di repository.** Semua kredensial dibaca dari environment variables; `.env` ada di `.gitignore` dan `.vercelignore`.
- **Row Level Security aktif** di semua tabel tanpa policy, sehingga key publik Supabase tidak bisa membaca data. Hanya backend (service_role key) yang mengakses database, dan semua otorisasi dilakukan di API.
- Password di-hash dengan scrypt (Werkzeug). Hash tidak pernah dikirim di response.
- JWT bertanda tangan HS256 dengan masa berlaku (default 24 jam). Role dibaca ulang dari database di setiap request, jadi perubahan role langsung berlaku.
- Semua input divalidasi (tipe, panjang, format email dan URL). Query database memakai client terparameter, tanpa SQL mentah. Konten frontend di-escape untuk mencegah XSS.
- Header keamanan (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`), `Cache-Control: no-store` untuk API, dan batas ukuran request 1 MB.
- Error database dipetakan ke status HTTP yang tepat; error tak terduga hanya dicatat di log Vercel dan tidak membocorkan detail ke klien.

**Batasan yang perlu diketahui:** belum ada rate limiting (untuk produksi nyata pertimbangkan Vercel Firewall atau Upstash), belum ada verifikasi email atau reset password, dan token disimpan di `localStorage` pada frontend. Untuk skala tugas akhir ini sudah memadai.

## 11. Troubleshooting

| Gejala | Penyebab dan solusi |
|--------|---------------------|
| `/api/health` menampilkan `not_configured` | Environment variable `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` belum diisi. Isi, lalu Redeploy di Vercel. |
| `/api/health` menampilkan `down` | Key salah, atau `schema.sql` belum dijalankan. Cek log di Vercel > Deployments > Functions. Jika memakai key baru berawalan `sb_secret_` dan gagal, pakai *legacy* `service_role` key. |
| Login mengembalikan 500 "Konfigurasi server belum lengkap" | `JWT_SECRET` kosong atau kurang dari 32 karakter. |
| Halaman tampil tapi tanpa gaya | Pastikan `"includeFiles": ["app/**"]` ada di `vercel.json`. |
| Cold start terasa lambat pada request pertama | Wajar untuk serverless; request berikutnya lebih cepat. |

## 12. Checklist Pengumpulan Tugas

- [x] Minimal 5 tabel dengan relasi foreign key (6 tabel, termasuk 2 pivot many-to-many)
- [x] Endpoint GET, POST, PUT/PATCH, dan DELETE
- [x] CRUD lengkap pada beberapa resource, JSON, status code tepat, pesan error jelas
- [x] Konfigurasi Vercel (`vercel.json`) dan environment variables
- [x] Koleksi Postman / Thunder Client untuk seluruh endpoint
- [x] Dokumentasi lengkap dan ERD
- [x] Tidak ada password atau secret key di repository
- [ ] **Yang harus Anda lakukan:** deploy ke Vercel, isi URL asli di README, dan ambil screenshot pengujian dari URL Vercel
