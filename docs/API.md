# Dokumentasi Endpoint SABDA LMS API

Ganti `https://nama-project.vercel.app` dengan URL deployment Vercel Anda.

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
