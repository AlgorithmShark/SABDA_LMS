# Tugas Akhir Learning Labs: Backend Development

## Tujuan Tugas

Kamu diminta membangun **REST API sederhana** berdasarkan ide project yang sudah kamu siapkan pada **Project Preparation Phase 1–2**. Tugas ini membuktikan bahwa kamu sudah bisa merancang database, membuat endpoint, men-deploy aplikasi, dan mendokumentasikannya.

Frontend/tampilan **tidak wajib**. Fokus penilaian ada di sisi backend.

---

## Ringkasan Requirement

| No | Komponen | Yang Harus Ada |
|----|----------|----------------|
| 1 | Database | Minimal **5 tabel** yang saling berelasi |
| 2 | Endpoint API | Menggunakan method **GET, POST, PUT/PATCH, DELETE** |
| 3 | Deployment | Sudah live di **Vercel** |
| 4 | Pengujian | Bisa diakses lewat **Thunder Client / Postman** |
| 5 | Dokumentasi | Dokumen cara memanggil setiap endpoint |
| 6 | Frontend | **Opsional** (tidak wajib) |

---

## 1. Skema Database (Minimal 5 Tabel)

**Yang dimaksud relational database:** tabel-tabel saling terhubung lewat **foreign key**, jadi bukan berdiri sendiri.

**Ketentuan:**

- Minimal 5 tabel, dan tiap tabel punya **primary key**.
- Minimal ada **relasi antar tabel** menggunakan foreign key. Disarankan memuat relasi *one-to-many*; relasi *many-to-many* (lewat tabel pivot) menjadi nilai tambah.
- Sertakan gambar **ERD Table** (diagram relasi antar tabel menggunakan drawsql.app atau dbdiagram.io) pada dokumentasi.

**Contoh gambaran relasi** (untuk project toko buku):

```
users ──< orders ──< order_items >── books >── categories
```

- Satu `user` punya banyak `orders`
- Satu `order` punya banyak `order_items`
- Satu `book` masuk ke satu `category`

> Ini hanya ilustrasi. Gunakan tema dari ide project milik kalian sendiri.

---

## 2. Layanan REST API (HTTP Method)

Setiap method punya fungsi yang berbeda. Project kamu harus memakai semuanya:

| Method | Fungsi | Contoh Endpoint | Status Sukses |
|--------|--------|-----------------|---------------|
| **GET** | Mengambil data | `GET /books`, `GET /books/1` | `200 OK` |
| **POST** | Menambah data baru | `POST /books` | `201 Created` |
| **PUT / PATCH** | Mengubah data (PUT: seluruh data, PATCH: sebagian) | `PUT /books/1` | `200 OK` |
| **DELETE** | Menghapus data | `DELETE /books/1` | `200 OK` / `204 No Content` |

**Ketentuan teknis:**

- Minimal **satu resource utama** memiliki CRUD lengkap (Create, Read, Update, Delete).
- Gunakan **format JSON** untuk request dan response.
- Gunakan **status code HTTP** yang tepat, misalnya `400` untuk input salah, `404` untuk data tidak ditemukan, `500` untuk error server.
- Berikan **pesan error yang jelas**, contoh: `{"error": "Buku tidak ditemukan"}`.

---

## 3. Deployment ke Vercel

- Project harus **sudah online** dan bisa diakses lewat URL publik, misalnya `https://nama-project.vercel.app`.
- Pastikan konfigurasi Vercel sudah benar (misalnya file `vercel.json`).
- **Jangan** menyimpan password database atau secret key langsung di kode. Gunakan **Environment Variables** di dashboard Vercel.
- Database harus berupa database yang bisa diakses dari internet (contoh: Supabase, Neon, atau layanan sejenis), bukan database lokal di laptopmu.

---

## 4. Pengujian dengan Thunder Client / Postman

API harus bisa dipanggil dari tools tersebut menggunakan **URL Vercel** (bukan `localhost`).

Siapkan bukti pengujian untuk **setiap endpoint**, berupa:

- Screenshot request dan response, **atau**
- Export collection Postman / Thunder Client (file `.json`)

---

## 5. Dokumentasi Pemanggilan API

Buat dokumentasi (bisa di `README.md`, Google Docs, atau Postman Documentation). Untuk **setiap endpoint**, tuliskan format berikut:

````
### Nama Endpoint
- Method       : POST
- URL          : https://nama-project.vercel.app/books
- Deskripsi    : Menambahkan buku baru
- Headers      : Content-Type: application/json
- Request Body :
  {
    "title": "Belajar Python",
    "price": 85000,
    "category_id": 1
  }
- Response Sukses (201):
  {
    "message": "Buku berhasil ditambahkan",
    "data": { "id": 10, "title": "Belajar Python" }
  }
- Response Error (400):
  {
    "error": "Field title wajib diisi"
  }
````

**Isi minimal dokumentasi:**

1. Deskripsi singkat project
2. ERD / skema database
3. Link URL deployment
4. Daftar seluruh endpoint (format di atas)
5. Cara menjalankan project secara lokal

---

## Yang Dikumpulkan

1. **Link repository** (GitHub)
2. **Link deployment** Vercel
3. **Dokumentasi API** (di README atau link terpisah)
4. **Bukti pengujian** (screenshot atau export collection)

---

## Checklist Sebelum Mengumpulkan

- [ ] Minimal 5 tabel dengan relasi foreign key
- [ ] Ada endpoint GET, POST, PUT/PATCH, dan DELETE
- [ ] API sudah live di Vercel dan bisa diakses publik
- [ ] Semua endpoint sudah dites lewat Postman / Thunder Client
- [ ] Dokumentasi lengkap dan ERD tersedia
- [ ] Tidak ada password atau secret key di repository