/* SABDA LMS - frontend SPA (vanilla JS, hash router). Semua data datang dari REST API /api. */
(() => {
  "use strict";

  // ---------- util ----------
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtDate = (d) => new Date(d).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" });
  const LEVELS = { beginner: "Pemula", intermediate: "Menengah", advanced: "Lanjutan" };
  const SPINES = ["#2745d8", "#1f7a5a", "#c2410c", "#7c3aed", "#0e7490", "#be185d"];
  const S = { token: localStorage.getItem("SABDA_token"), user: null, cats: [], filter: { q: "", category_id: "" } };
  const app = $("#app");

  class ApiError extends Error {
    constructor(message, status) { super(message); this.status = status; }
  }

  async function api(path, { method = "GET", body } = {}) {
    const headers = {};
    if (body) headers["Content-Type"] = "application/json";
    if (S.token) headers.Authorization = "Bearer " + S.token;
    let res;
    try {
      res = await fetch("/api" + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
    } catch {
      throw new ApiError("Tidak dapat terhubung ke server. Periksa koneksi Anda.", 0);
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      if (res.status === 401 && S.token) { setSession(null); toast("Sesi berakhir, silakan masuk lagi", "error"); location.hash = "#/login"; }
      throw new ApiError(data.error || "Terjadi kesalahan", res.status);
    }
    return data;
  }

  function toast(msg, type = "") {
    const el = document.createElement("div");
    el.className = "toast " + type;
    el.textContent = msg;
    $("#toasts").append(el);
    setTimeout(() => el.remove(), 3800);
  }

  function setSession(token, user = null) {
    S.token = token; S.user = user;
    token ? localStorage.setItem("SABDA_token", token) : localStorage.removeItem("SABDA_token");
    renderNav();
  }

  // ---------- render helpers ----------
  const inline = (t) => esc(t).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  function md(src) {
    const out = [];
    String(src || "").replace(/\r/g, "").split("```").forEach((part, i) => {
      if (i % 2) { out.push(`<pre><code>${esc(part.replace(/^\n/, "").replace(/\n$/, ""))}</code></pre>`); return; }
      part.split(/\n{2,}/).forEach((b) => {
        b = b.trim();
        if (!b) return;
        const h = b.match(/^(#{1,3})\s+(.*)$/);
        if (h && !b.includes("\n")) { const n = h[1].length + 1; out.push(`<h${n}>${inline(h[2])}</h${n}>`); return; }
        const lines = b.split("\n");
        if (lines.every((l) => /^[-*]\s+/.test(l))) out.push("<ul>" + lines.map((l) => `<li>${inline(l.replace(/^[-*]\s+/, ""))}</li>`).join("") + "</ul>");
        else out.push("<p>" + lines.map(inline).join("<br>") + "</p>");
      });
    });
    return out.join("");
  }
  function video(url) {
    if (!url) return "";
    const m = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([\w-]{11})/);
    if (m) return `<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${m[1]}" title="Video pelajaran" allowfullscreen loading="lazy"></iframe></div>`;
    return `<p><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Buka video pelajaran</a></p>`;
  }
  const bar = (p) => `<div class="progress-label"><span>${p.completed} dari ${p.total} pelajaran</span><strong>${p.percent}%</strong></div>
    <div class="bar" role="progressbar" aria-valuenow="${p.percent}" aria-valuemin="0" aria-valuemax="100"><i style="width:${p.percent}%"></i></div>`;
  const empty = (text, cta = "") => `<div class="empty"><p>${esc(text)}</p>${cta}</div>`;
  const spine = (id) => SPINES[(id || 0) % SPINES.length];

  function courseCard(c) {
    return `<a class="course" href="#/course/${c.id}" style="--spine:${spine(c.category_id)}">
      <span class="cat">${esc(c.category_name)}${c.is_published ? "" : ' <span class="badge draft">Draf</span>'}</span>
      <h3>${esc(c.title)}</h3>
      <p class="desc">${esc(c.description)}</p>
      <div class="facts"><span>${LEVELS[c.level]}</span><span>${c.lesson_count} pelajaran</span><span>Oleh ${esc(c.instructor_name)}</span></div>
    </a>`;
  }

  function renderNav() {
    const u = S.user, here = location.hash || "#/";
    const link = (href, text) => `<a href="${href}" ${here === href ? 'aria-current="page"' : ""}>${text}</a>`;
    let html = link("#/", "Katalog");
    if (u && u.role === "student") html += link("#/learning", "Belajar saya");
    if (u && (u.role === "instructor" || u.role === "admin")) html += link("#/teach", "Mengajar");
    if (u && u.role === "admin") html += link("#/admin", "Admin");
    html += u
      ? `<span class="who">${esc(u.name)}</span><button class="btn ghost sm" data-action="logout">Keluar</button>`
      : link("#/login", "Masuk") + '<a class="btn primary sm" href="#/register">Daftar</a>';
    $("#nav").innerHTML = html;
  }

  // ---------- modal form ----------
  const modal = $("#modal");
  function fieldHTML(f) {
    const v = f.value ?? "", id = "f-" + f.name, req = f.required ? "required" : "";
    if (f.type === "checkbox") return `<div class="field check"><label><input type="checkbox" name="${f.name}" ${f.value ? "checked" : ""}> ${esc(f.label)}</label></div>`;
    let input;
    if (f.type === "select") input = `<select id="${id}" name="${f.name}" ${req}>${f.options.map(([val, text]) => `<option value="${esc(val)}" ${String(val) === String(v) ? "selected" : ""}>${esc(text)}</option>`).join("")}</select>`;
    else if (f.type === "textarea") input = `<textarea id="${id}" name="${f.name}" ${req}>${esc(v)}</textarea>`;
    else input = `<input id="${id}" name="${f.name}" type="${f.type || "text"}" value="${esc(v)}" ${req} ${f.type === "password" ? 'autocomplete="new-password"' : ""}>`;
    return `<div class="field"><label for="${id}">${esc(f.label)}</label>${input}${f.hint ? `<p class="hint">${esc(f.hint)}</p>` : ""}</div>`;
  }
  function openForm({ title, fields, submit = "Simpan", onSubmit }) {
    $("#modal-title").textContent = title;
    $("#modal-fields").innerHTML = fields.map(fieldHTML).join("");
    $("#modal-error").hidden = true;
    $("#modal-submit").textContent = submit;
    modal._onSubmit = async (form) => {
      const values = {};
      fields.forEach((f) => { values[f.name] = f.type === "checkbox" ? form.elements[f.name].checked : form.elements[f.name].value; });
      await onSubmit(values);
    };
    modal.showModal();
    const first = $("input, select, textarea", $("#modal-fields")); first && first.focus();
  }
  $("#modal-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = $("#modal-submit"); btn.disabled = true;
    try { await modal._onSubmit(e.target); modal.close(); }
    catch (err) { const box = $("#modal-error"); box.textContent = err.message; box.hidden = false; }
    finally { btn.disabled = false; }
  });

  // ---------- views ----------
  async function categories() {
    if (!S.cats.length) S.cats = (await api("/categories")).data;
    return S.cats;
  }

  async function homeView(root) {
    const [cats, stats] = await Promise.all([categories(), api("/stats")]);
    const st = stats.data;
    root.innerHTML = `
      <section class="hero">
        <h1>Mau belajar apa hari ini?</h1>
        <p class="lede">SABDA punya ${st.courses} kursus dengan ${st.lessons} pelajaran. Saat ini ${st.students} siswa sedang belajar.</p>
        <label class="sr" for="q">Cari kursus</label>
        <input id="q" class="search" type="search" placeholder="Cari judul kursus, misalnya Python" value="${esc(S.filter.q)}" autocomplete="off">
      </section>
      <div class="filters" role="group" aria-label="Filter kategori">
        <button data-action="filter-cat" data-id="" aria-pressed="${S.filter.category_id === ""}">Semua</button>
        ${cats.map((c) => `<button data-action="filter-cat" data-id="${c.id}" aria-pressed="${String(S.filter.category_id) === String(c.id)}">${esc(c.name)}</button>`).join("")}
      </div>
      <div id="grid" class="grid" aria-live="polite"></div>`;
    let timer;
    $("#q").addEventListener("input", (e) => { S.filter.q = e.target.value; clearTimeout(timer); timer = setTimeout(loadGrid, 300); });
    await loadGrid();
  }

  async function loadGrid() {
    const grid = $("#grid"); if (!grid) return;
    const p = new URLSearchParams({ per_page: 50 });
    if (S.filter.q) p.set("q", S.filter.q);
    if (S.filter.category_id) p.set("category_id", S.filter.category_id);
    try {
      const { data } = await api("/courses?" + p);
      grid.innerHTML = data.length ? data.map(courseCard).join("") : empty("Belum ada kursus yang cocok. Coba kata kunci atau kategori lain.");
    } catch (e) { grid.innerHTML = empty(e.message); }
  }

  async function courseView(root, id) {
    const { data: c } = await api(`/courses/${id}`);
    const u = S.user, firstOpen = c.lessons.find((l) => !l.is_completed) || c.lessons[0];
    let cta = "";
    if (!u) cta = `<a class="btn primary" href="#/login">Masuk untuk mendaftar</a>`;
    else if (c.can_manage) cta = `<a class="btn primary" href="#/teach/${c.id}">Kelola kursus</a>`;
    else if (u.role === "student" && c.is_enrolled) cta = (firstOpen ? `<a class="btn primary" href="#/lesson/${firstOpen.id}">Lanjutkan belajar</a>` : "") + `<button class="btn danger" data-action="unenroll" data-id="${c.id}">Keluar dari kursus</button>`;
    else if (u.role === "student") cta = `<button class="btn primary" data-action="enroll" data-id="${c.id}">Daftar kursus</button>`;
    const canOpen = c.is_enrolled || c.can_manage;
    root.innerHTML = `
      <div class="split">
        <article>
          <p class="muted">${esc(c.category_name)} ${c.is_published ? "" : '<span class="badge draft">Draf</span>'}</p>
          <h1>${esc(c.title)}</h1>
          <p class="reading" style="font-size:1.15rem">${esc(c.description) || "Belum ada deskripsi."}</p>
          <div class="facts"><span>${LEVELS[c.level]}</span><span>${c.lesson_count} pelajaran</span><span>${c.student_count} siswa</span><span>Pengajar: ${esc(c.instructor_name)}</span></div>
          <div class="actions">${cta}</div>
        </article>
        <aside class="panel">
          <h2>Isi kursus</h2>
          ${c.lessons.length ? `<ol class="lesson-list" style="list-style:none">${c.lessons.map((l, i) => {
            const mark = c.is_enrolled ? `<span class="tick" aria-label="${l.is_completed ? "Selesai" : "Belum selesai"}">${l.is_completed ? "&#10003;" : ""}</span>` : `<span class="pos">${i + 1}</span>`;
            return `<li>${canOpen ? `<a href="#/lesson/${l.id}">${mark}${esc(l.title)}</a>` : `<span class="row">${mark}${esc(l.title)}</span>`}</li>`;
          }).join("")}</ol>` : '<p class="muted">Pelajaran belum ditambahkan.</p>'}
          ${!canOpen && c.lessons.length ? '<p class="hint">Daftar kursus untuk membuka isi pelajaran.</p>' : ""}
        </aside>
      </div>`;
  }

  async function lessonView(root, id) {
    const { data: l } = await api(`/lessons/${id}`);
    const { data: c } = await api(`/courses/${l.course_id}`);
    const student = S.user && S.user.role === "student";
    root.innerHTML = `
      <p><a href="#/course/${c.id}">&larr; ${esc(c.title)}</a></p>
      <div class="split">
        <article>
          <h1>${esc(l.title)}</h1>
          ${video(l.video_url)}
          <div class="reading">${md(l.content) || '<p class="muted">Pelajaran ini belum memiliki materi tertulis.</p>'}</div>
          <div class="actions">${student ? (l.is_completed
            ? `<button class="btn ghost" data-action="uncomplete" data-id="${l.id}">Batalkan tanda selesai</button>`
            : `<button class="btn primary" data-action="complete" data-id="${l.id}" data-next="${l.next_lesson_id || ""}">Tandai selesai</button>`) : ""}</div>
          <div class="pager">
            ${l.prev_lesson_id ? `<a class="btn ghost" href="#/lesson/${l.prev_lesson_id}">&larr; Sebelumnya</a>` : "<span></span>"}
            ${l.next_lesson_id ? `<a class="btn ghost" href="#/lesson/${l.next_lesson_id}">Berikutnya &rarr;</a>` : "<span></span>"}
          </div>
        </article>
        <aside class="panel"><h2>Daftar pelajaran</h2>
          <ol class="lesson-list" style="list-style:none">${c.lessons.map((x) => `<li class="${x.id === l.id ? "on" : ""}"><a href="#/lesson/${x.id}"><span class="tick">${x.is_completed ? "&#10003;" : ""}</span>${esc(x.title)}</a></li>`).join("")}</ol>
        </aside>
      </div>`;
  }

  function authView(root, mode) {
    const reg = mode === "register";
    root.innerHTML = `
      <section class="narrow">
        <h1>${reg ? "Buat akun" : "Masuk"}</h1>
        <form id="auth-form" novalidate>
          ${reg ? '<div class="field"><label for="name">Nama lengkap</label><input id="name" name="name" required autocomplete="name"></div>' : ""}
          <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" required autocomplete="email"></div>
          <div class="field"><label for="password">Password</label><input id="password" name="password" type="password" required minlength="8" autocomplete="${reg ? "new-password" : "current-password"}">${reg ? '<p class="hint">Minimal 8 karakter.</p>' : ""}</div>
          <p class="form-error" id="auth-error" role="alert" hidden></p>
          <button class="btn primary" type="submit">${reg ? "Daftar sebagai siswa" : "Masuk"}</button>
        </form>
        <p class="muted" style="margin-top:16px">${reg ? 'Sudah punya akun? <a href="#/login">Masuk</a>' : 'Belum punya akun? <a href="#/register">Daftar gratis</a>'}</p>
      </section>`;
    $("#auth-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const f = e.target, btn = $("button", f), box = $("#auth-error");
      btn.disabled = true; box.hidden = true;
      try {
        const body = { email: f.email.value, password: f.password.value };
        if (reg) body.name = f.name.value;
        const { data } = await api(reg ? "/auth/register" : "/auth/login", { method: "POST", body });
        setSession(data.token, data.user);
        toast(`Halo, ${data.user.name}`);
        location.hash = data.user.role === "student" ? "#/learning" : data.user.role === "admin" ? "#/admin" : "#/teach";
      } catch (err) { box.textContent = err.message; box.hidden = false; btn.disabled = false; }
    });
  }

  async function learningView(root) {
    if (!guard(root, "student")) return;
    const { data } = await api("/enrollments/me");
    root.innerHTML = `<div class="page-head"><h1>Belajar saya</h1></div>` + (data.length
      ? `<div class="grid">${data.map((c) => `<a class="course" href="#/course/${c.id}" style="--spine:${spine(c.category_id)}">
          <span class="cat">${esc(c.category_name)}</span><h3>${esc(c.title)}</h3>${bar(c.progress)}</a>`).join("")}</div>`
      : empty("Anda belum mendaftar ke kursus mana pun.", '<a class="btn primary" href="#/">Jelajahi katalog</a>'));
  }

  async function teachView(root) {
    if (!guard(root, "instructor", "admin")) return;
    const admin = S.user.role === "admin";
    const { data } = await api("/courses?per_page=50&scope=" + (admin ? "all" : "mine"));
    root.innerHTML = `<div class="page-head"><h1>${admin ? "Semua kursus" : "Kursus saya"}</h1><button class="btn primary" data-action="new-course">Kursus baru</button></div>` +
      (data.length ? `<div class="table-wrap"><table><thead><tr><th>Judul</th><th>Kategori</th><th>Status</th><th class="right">Pelajaran</th><th class="right">Siswa</th><th></th></tr></thead><tbody>
        ${data.map((c) => `<tr><td><a href="#/teach/${c.id}"><strong>${esc(c.title)}</strong></a>${admin ? `<br><span class="muted">${esc(c.instructor_name)}</span>` : ""}</td><td>${esc(c.category_name)}</td>
          <td>${c.is_published ? '<span class="badge">Terbit</span>' : '<span class="badge draft">Draf</span>'}</td><td class="right">${c.lesson_count}</td><td class="right">${c.student_count}</td>
          <td class="right"><a class="btn ghost sm" href="#/teach/${c.id}">Kelola</a><button class="btn danger sm" data-action="delete-course" data-id="${c.id}">Hapus</button></td></tr>`).join("")}
        </tbody></table></div>` : empty("Anda belum membuat kursus.", '<button class="btn primary" data-action="new-course">Buat kursus pertama</button>'));
  }

  async function teachCourseView(root, id) {
    if (!guard(root, "instructor", "admin")) return;
    const [{ data: c }, { data: lessons }, { data: students }] = await Promise.all([
      api(`/courses/${id}`), api(`/courses/${id}/lessons`), api(`/courses/${id}/students`)]);
    root.innerHTML = `
      <p><a href="#/teach">&larr; Semua kursus</a></p>
      <div class="page-head"><div><h1>${esc(c.title)}</h1><p class="muted">${esc(c.category_name)}, ${LEVELS[c.level]} ${c.is_published ? '<span class="badge">Terbit</span>' : '<span class="badge draft">Draf</span>'}</p></div>
        <div><a class="btn ghost" href="#/course/${c.id}">Lihat halaman publik</a> <button class="btn" data-action="edit-course" data-id="${c.id}">Ubah kursus</button></div></div>
      <div class="page-head"><h2>Pelajaran</h2><button class="btn primary" data-action="new-lesson" data-id="${c.id}">Tambah pelajaran</button></div>
      ${lessons.length ? `<div class="table-wrap"><table><thead><tr><th class="right">Urutan</th><th>Judul</th><th></th></tr></thead><tbody>
        ${lessons.map((l) => `<tr><td class="right">${l.position}</td><td>${esc(l.title)}</td><td class="right"><button class="btn ghost sm" data-action="edit-lesson" data-id="${l.id}" data-course="${c.id}">Ubah</button><button class="btn danger sm" data-action="delete-lesson" data-id="${l.id}">Hapus</button></td></tr>`).join("")}</tbody></table></div>` : empty("Belum ada pelajaran. Tambahkan pelajaran pertama agar siswa bisa mulai belajar.")}
      <h2 style="margin-top:36px">Siswa terdaftar</h2>
      ${students.length ? `<div class="table-wrap"><table><thead><tr><th>Nama</th><th>Email</th><th>Bergabung</th><th style="min-width:160px">Progres</th></tr></thead><tbody>
        ${students.map((s) => `<tr><td>${esc(s.name)}</td><td>${esc(s.email)}</td><td>${fmtDate(s.enrolled_at)}</td><td>${bar(s)}</td></tr>`).join("")}</tbody></table></div>` : empty("Belum ada siswa yang mendaftar.")}`;
    app._lessons = lessons; app._course = c;
  }

  async function adminView(root) {
    if (!guard(root, "admin")) return;
    S.cats = [];
    const [cats, users] = await Promise.all([categories(), api("/users?per_page=100")]);
    root.innerHTML = `
      <div class="page-head"><h1>Administrasi</h1></div>
      <div class="page-head"><h2>Kategori</h2><button class="btn primary" data-action="new-cat">Kategori baru</button></div>
      <div class="table-wrap"><table><thead><tr><th>Nama</th><th>Deskripsi</th><th></th></tr></thead><tbody>
        ${cats.map((c) => `<tr><td><strong>${esc(c.name)}</strong></td><td class="muted">${esc(c.description)}</td><td class="right"><button class="btn ghost sm" data-action="edit-cat" data-id="${c.id}">Ubah</button><button class="btn danger sm" data-action="delete-cat" data-id="${c.id}">Hapus</button></td></tr>`).join("")}</tbody></table></div>
      <div class="page-head"><h2>Pengguna (${users.meta.total})</h2></div>
      <div class="table-wrap"><table><thead><tr><th>Nama</th><th>Email</th><th>Role</th><th>Terdaftar</th><th></th></tr></thead><tbody>
        ${users.data.map((u) => `<tr><td>${esc(u.name)}</td><td>${esc(u.email)}</td>
          <td><label class="sr" for="role-${u.id}">Role ${esc(u.name)}</label><select id="role-${u.id}" data-change="role" data-id="${u.id}" ${u.id === S.user.id ? "disabled" : ""}>
            ${["student", "instructor", "admin"].map((r) => `<option ${u.role === r ? "selected" : ""}>${r}</option>`).join("")}</select></td>
          <td>${fmtDate(u.created_at)}</td><td class="right">${u.id === S.user.id ? "" : `<button class="btn danger sm" data-action="delete-user" data-id="${u.id}">Hapus</button>`}</td></tr>`).join("")}</tbody></table></div>`;
    app._cats = cats;
  }

  function guard(root, ...roles) {
    if (!S.user) { location.hash = "#/login"; return false; }
    if (!roles.includes(S.user.role)) { root.innerHTML = empty("Halaman ini tidak tersedia untuk role Anda.", '<a class="btn primary" href="#/">Kembali ke katalog</a>'); return false; }
    return true;
  }

  // ---------- form definitions ----------
  async function courseForm(course) {
    const cats = await categories();
    openForm({
      title: course ? "Ubah kursus" : "Kursus baru",
      fields: [
        { name: "title", label: "Judul", required: true, value: course?.title },
        { name: "description", label: "Deskripsi", type: "textarea", value: course?.description },
        { name: "category_id", label: "Kategori", type: "select", options: cats.map((c) => [c.id, c.name]), value: course?.category_id },
        { name: "level", label: "Level", type: "select", options: Object.entries(LEVELS), value: course?.level || "beginner" },
        { name: "is_published", label: "Terbitkan kursus (terlihat di katalog)", type: "checkbox", value: course?.is_published },
      ],
      onSubmit: async (v) => {
        v.category_id = Number(v.category_id);
        await api(course ? `/courses/${course.id}` : "/courses", { method: course ? "PUT" : "POST", body: v });
        toast(course ? "Kursus diperbarui" : "Kursus dibuat"); render();
      },
    });
  }
  function lessonForm(courseId, lesson) {
    openForm({
      title: lesson ? "Ubah pelajaran" : "Pelajaran baru",
      fields: [
        { name: "title", label: "Judul pelajaran", required: true, value: lesson?.title },
        { name: "content", label: "Materi", type: "textarea", value: lesson?.content, hint: "Mendukung ## judul, - daftar, **tebal**, `kode`, dan blok kode dengan tiga backtick." },
        { name: "video_url", label: "Tautan video (opsional)", type: "url", value: lesson?.video_url, hint: "URL YouTube akan ditampilkan langsung di halaman." },
        { name: "position", label: "Urutan", type: "number", value: lesson?.position, hint: "Kosongkan untuk menaruh di akhir." },
      ],
      onSubmit: async (v) => {
        const body = { title: v.title, content: v.content, video_url: v.video_url };
        if (v.position) body.position = Number(v.position);
        await api(lesson ? `/lessons/${lesson.id}` : `/courses/${courseId}/lessons`, { method: lesson ? "PUT" : "POST", body });
        toast(lesson ? "Pelajaran diperbarui" : "Pelajaran ditambahkan"); render();
      },
    });
  }
  function catForm(cat) {
    openForm({
      title: cat ? "Ubah kategori" : "Kategori baru",
      fields: [{ name: "name", label: "Nama kategori", required: true, value: cat?.name }, { name: "description", label: "Deskripsi", type: "textarea", value: cat?.description }],
      onSubmit: async (v) => { await api(cat ? `/categories/${cat.id}` : "/categories", { method: cat ? "PUT" : "POST", body: v }); toast("Kategori disimpan"); render(); },
    });
  }

  // ---------- actions (event delegation) ----------
  const run = async (fn, okMsg) => { try { await fn(); if (okMsg) toast(okMsg); render(); } catch (e) { toast(e.message, "error"); } };
  const remove = (what, path) => confirm(`Hapus ${what}? Tindakan ini tidak bisa dibatalkan.`) && run(() => api(path, { method: "DELETE" }), "Berhasil dihapus");

  const actions = {
    logout: () => { setSession(null); toast("Anda sudah keluar"); location.hash = "#/"; },
    "close-modal": () => modal.close(),
    "filter-cat": (el) => { S.filter.category_id = el.dataset.id; document.querySelectorAll(".filters button").forEach((b) => b.setAttribute("aria-pressed", b === el)); loadGrid(); },
    enroll: (el) => run(() => api(`/courses/${el.dataset.id}/enroll`, { method: "POST" }), "Berhasil mendaftar"),
    unenroll: (el) => confirm("Keluar dari kursus ini? Progres belajar Anda akan dihapus.") && run(() => api(`/courses/${el.dataset.id}/enroll`, { method: "DELETE" }), "Anda keluar dari kursus"),
    complete: (el) => run(async () => { await api(`/lessons/${el.dataset.id}/complete`, { method: "POST" }); if (el.dataset.next) location.hash = "#/lesson/" + el.dataset.next; }, "Pelajaran selesai"),
    uncomplete: (el) => run(() => api(`/lessons/${el.dataset.id}/complete`, { method: "DELETE" })),
    "new-course": () => courseForm(),
    "edit-course": async (el) => courseForm((await api(`/courses/${el.dataset.id}`)).data),
    "delete-course": (el) => remove("kursus beserta pelajarannya", `/courses/${el.dataset.id}`),
    "new-lesson": (el) => lessonForm(el.dataset.id),
    "edit-lesson": (el) => lessonForm(el.dataset.course, (app._lessons || []).find((l) => l.id == el.dataset.id)),
    "delete-lesson": (el) => remove("pelajaran", `/lessons/${el.dataset.id}`),
    "new-cat": () => catForm(),
    "edit-cat": (el) => catForm((app._cats || []).find((c) => c.id == el.dataset.id)),
    "delete-cat": (el) => remove("kategori", `/categories/${el.dataset.id}`),
    "delete-user": (el) => remove("pengguna", `/users/${el.dataset.id}`),
  };
  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-action]");
    if (el && actions[el.dataset.action]) { e.preventDefault(); actions[el.dataset.action](el); }
  });
  document.addEventListener("change", (e) => {
    const el = e.target.closest("[data-change='role']");
    if (el) run(() => api(`/users/${el.dataset.id}`, { method: "PATCH", body: { role: el.value } }), "Role diperbarui");
  });

  // ---------- router ----------
  const routes = [
    [/^\/?$/, homeView], [/^\/course\/(\d+)$/, courseView], [/^\/lesson\/(\d+)$/, lessonView],
    [/^\/login$/, (r) => authView(r, "login")], [/^\/register$/, (r) => authView(r, "register")],
    [/^\/learning$/, learningView], [/^\/teach$/, teachView], [/^\/teach\/(\d+)$/, teachCourseView], [/^\/admin$/, adminView],
  ];
  let renderId = 0;
  async function render() {
    const id = ++renderId, path = location.hash.slice(1) || "/";
    const root = document.createElement("div");
    app.replaceChildren(root);          // tampilan lama yang telat selesai hanya menulis ke wadah yang sudah terlepas
    renderNav();
    for (const [re, view] of routes) {
      const m = path.match(re);
      if (!m) continue;
      try { await view(root, ...m.slice(1)); }
      catch (e) { if (id === renderId) root.innerHTML = empty(e.status === 404 ? "Halaman atau data tidak ditemukan." : e.message, '<a class="btn primary" href="#/">Kembali ke katalog</a>'); }
      return;
    }
    root.innerHTML = empty("Halaman tidak ditemukan.", '<a class="btn primary" href="#/">Kembali ke katalog</a>');
  }
  let lastPath = null;
  window.addEventListener("hashchange", async () => { await render(); if (location.hash !== lastPath) { window.scrollTo(0, 0); lastPath = location.hash; } });

  (async function init() {
    app.innerHTML = '<p class="loading">Memuat...</p>';
    if (S.token) { try { S.user = (await api("/auth/me")).data; } catch { setSession(null); } }
    lastPath = location.hash;
    render();
  })();
})();
