-- =====================================================================
-- SABDA LMS - Skema Database (PostgreSQL / Supabase)
-- Jalankan di: Supabase Dashboard > SQL Editor > New query > Run
-- Aman dijalankan ulang (idempotent).
-- =====================================================================

-- 1. users --------------------------------------------------------------
create table if not exists users (
  id            bigint generated always as identity primary key,
  name          text        not null check (char_length(name) between 2 and 100),
  email         text        not null unique check (email = lower(email)),
  password_hash text        not null,
  role          text        not null default 'student' check (role in ('admin', 'instructor', 'student')),
  created_at    timestamptz not null default now()
);

-- 2. categories ---------------------------------------------------------
create table if not exists categories (
  id          bigint generated always as identity primary key,
  name        text not null unique check (char_length(name) between 2 and 80),
  description text not null default ''
);

-- 3. courses (one-to-many: category -> courses, instructor -> courses) ---
create table if not exists courses (
  id            bigint generated always as identity primary key,
  title         text        not null check (char_length(title) between 3 and 150),
  description   text        not null default '',
  category_id   bigint      not null references categories (id) on delete restrict,
  instructor_id bigint      not null references users (id)      on delete restrict,
  level         text        not null default 'beginner' check (level in ('beginner', 'intermediate', 'advanced')),
  is_published  boolean     not null default false,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- 4. lessons (one-to-many: course -> lessons) ---------------------------
create table if not exists lessons (
  id         bigint generated always as identity primary key,
  course_id  bigint      not null references courses (id) on delete cascade,
  title      text        not null check (char_length(title) between 3 and 150),
  content    text        not null default '',
  video_url  text,
  position   integer     not null default 1 check (position > 0),
  created_at timestamptz not null default now()
);

-- 5. enrollments (pivot many-to-many: users <-> courses) ----------------
create table if not exists enrollments (
  id          bigint generated always as identity primary key,
  user_id     bigint      not null references users (id)   on delete cascade,
  course_id   bigint      not null references courses (id) on delete cascade,
  enrolled_at timestamptz not null default now(),
  unique (user_id, course_id)
);

-- 6. lesson_progress (pivot many-to-many: users <-> lessons) ------------
create table if not exists lesson_progress (
  id           bigint generated always as identity primary key,
  user_id      bigint      not null references users (id)   on delete cascade,
  lesson_id    bigint      not null references lessons (id) on delete cascade,
  completed_at timestamptz not null default now(),
  unique (user_id, lesson_id)
);

-- Index untuk kolom foreign key / pencarian ------------------------------
create index if not exists idx_courses_category    on courses (category_id);
create index if not exists idx_courses_instructor  on courses (instructor_id);
create index if not exists idx_courses_published   on courses (is_published, created_at desc);
create index if not exists idx_lessons_course_pos  on lessons (course_id, position);
create index if not exists idx_enrollments_course  on enrollments (course_id);
create index if not exists idx_progress_lesson     on lesson_progress (lesson_id);

-- View statistik kursus (dipakai API agar hitungan akurat & cepat) -------
create or replace view course_stats as
select c.id as course_id,
       (select count(*) from lessons l     where l.course_id = c.id)::int as lesson_count,
       (select count(*) from enrollments e where e.course_id = c.id)::int as student_count
from courses c;

-- Keamanan: aktifkan Row Level Security tanpa policy. ---------------------
-- Akibatnya key "anon"/"authenticated" TIDAK bisa membaca/menulis data lewat
-- REST publik Supabase. Hanya backend Flask (service_role key) yang dapat
-- mengakses data, dan semua otorisasi dilakukan di API.
alter table users           enable row level security;
alter table categories      enable row level security;
alter table courses         enable row level security;
alter table lessons         enable row level security;
alter table enrollments     enable row level security;
alter table lesson_progress enable row level security;
revoke all on course_stats from anon, authenticated;
