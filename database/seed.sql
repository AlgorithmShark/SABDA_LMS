-- =====================================================================
-- SABDA LMS - Data contoh (OPSIONAL, untuk demo / pengujian)
-- Jalankan SETELAH schema.sql. Password semua akun demo: Password123!
-- PENTING: hapus akun demo atau ganti password-nya sebelum dipakai nyata.
-- =====================================================================

insert into categories (name, description) values
  ('Pemrograman', 'Belajar menulis kode dari dasar hingga membangun aplikasi'),
  ('Desain', 'Prinsip desain antarmuka dan pengalaman pengguna'),
  ('Data', 'Basis data, SQL, dan analisis data')
on conflict (name) do nothing;

insert into users (name, email, password_hash, role) values
  ('Admin Pelita',    'admin@lms.test',      'scrypt:32768:8:1$Xly0SGcnwgpaAonX$eb920544da23df38ea0a481e88caed48bf57243ba91e46ad08a265a1196eb7bbcf8ed1016a05142392c683108f559e9daa5d025060773e3410d05a0dc061d380', 'admin'),
  ('Bu Sari Pengajar','instructor@lms.test', 'scrypt:32768:8:1$Xly0SGcnwgpaAonX$eb920544da23df38ea0a481e88caed48bf57243ba91e46ad08a265a1196eb7bbcf8ed1016a05142392c683108f559e9daa5d025060773e3410d05a0dc061d380', 'instructor'),
  ('Budi Siswa',      'student@lms.test',    'scrypt:32768:8:1$Xly0SGcnwgpaAonX$eb920544da23df38ea0a481e88caed48bf57243ba91e46ad08a265a1196eb7bbcf8ed1016a05142392c683108f559e9daa5d025060773e3410d05a0dc061d380', 'student')
on conflict (email) do nothing;

do $$
declare
  v_teacher bigint; v_student bigint; v_py bigint; v_ui bigint; v_sql bigint; v_l1 bigint;
begin
  if exists (select 1 from courses) then return; end if;
  select id into v_teacher from users where email = 'instructor@lms.test';
  select id into v_student from users where email = 'student@lms.test';

  insert into courses (title, description, category_id, instructor_id, level, is_published)
  values ('Dasar Pemrograman Python', 'Mulai dari variabel, percabangan, hingga fungsi. Cocok untuk yang belum pernah menulis kode.',
          (select id from categories where name = 'Pemrograman'), v_teacher, 'beginner', true) returning id into v_py;
  insert into courses (title, description, category_id, instructor_id, level, is_published)
  values ('Desain Antarmuka untuk Pemula', 'Pelajari hierarki visual, tipografi, dan warna agar tampilan aplikasi mudah dipakai.',
          (select id from categories where name = 'Desain'), v_teacher, 'beginner', true) returning id into v_ui;
  insert into courses (title, description, category_id, instructor_id, level, is_published)
  values ('Pengantar Basis Data dan SQL', 'Memahami tabel, relasi, dan menulis query SELECT, INSERT, UPDATE, DELETE.',
          (select id from categories where name = 'Data'), v_teacher, 'intermediate', true) returning id into v_sql;
  insert into courses (title, description, category_id, instructor_id, level, is_published)
  values ('Machine Learning Dasar (Draft)', 'Kursus ini masih disusun dan belum dipublikasikan.',
          (select id from categories where name = 'Data'), v_teacher, 'advanced', false);

  insert into lessons (course_id, title, content, video_url, position) values
    (v_py, 'Mengenal Python dan Variabel',
     E'## Apa itu variabel?\n\nVariabel adalah tempat menyimpan nilai. Di Python, Anda cukup menulis nama dan nilainya.\n\n```\nnama = "Budi"\numur = 17\nprint(nama, umur)\n```\n\nTipe data yang sering dipakai:\n\n- str untuk teks\n- int untuk bilangan bulat\n- float untuk bilangan desimal\n- bool untuk True atau False', null, 1),
    (v_py, 'Percabangan if dan else',
     E'## Mengambil keputusan\n\nGunakan `if` untuk menjalankan kode hanya jika syarat terpenuhi.\n\n```\nnilai = 80\nif nilai >= 75:\n    print("Lulus")\nelse:\n    print("Remedial")\n```\n\nPerhatikan indentasi: Python memakai spasi untuk menandai blok kode.', null, 2),
    (v_py, 'Fungsi dan Pengulangan',
     E'## Fungsi\n\nFungsi membungkus kode agar bisa dipakai ulang.\n\n```\ndef sapa(nama):\n    return "Halo, " + nama\n\nfor n in ["Ani", "Budi"]:\n    print(sapa(n))\n```', null, 3),
    (v_ui, 'Hierarki Visual',
     E'## Mata mengikuti ukuran dan kontras\n\nElemen yang paling penting harus paling mudah dilihat. Atur lewat ukuran, ketebalan, warna, dan jarak.\n\n- Satu halaman, satu aksi utama\n- Kelompokkan konten yang berhubungan\n- Beri ruang kosong secukupnya', null, 1),
    (v_ui, 'Tipografi yang Terbaca',
     E'## Memilih huruf\n\nGunakan maksimal dua jenis huruf. Panjang baris ideal 45 sampai 75 karakter dan tinggi baris sekitar 1,5 kali ukuran huruf.', null, 2),
    (v_sql, 'Tabel, Baris, dan Kolom',
     E'## Dasar basis data relasional\n\nData disimpan dalam tabel. Setiap baris adalah satu catatan, setiap kolom adalah atribut. Primary key mengidentifikasi baris secara unik.', null, 1),
    (v_sql, 'Query SELECT',
     E'## Mengambil data\n\n```\nselect nama, email\nfrom pengguna\nwhere peran = \'siswa\'\norder by nama;\n```', null, 2),
    (v_sql, 'Relasi dan JOIN',
     E'## Menggabungkan tabel\n\nForeign key menghubungkan dua tabel. Gunakan JOIN untuk membaca data dari keduanya sekaligus.\n\n```\nselect k.judul, p.nama\nfrom kursus k\njoin pengguna p on p.id = k.pengajar_id;\n```', null, 3);

  insert into enrollments (user_id, course_id) values (v_student, v_py), (v_student, v_sql);
  select id into v_l1 from lessons where course_id = v_py and position = 1;
  insert into lesson_progress (user_id, lesson_id) values (v_student, v_l1);
end $$;
