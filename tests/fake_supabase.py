"""Supabase tiruan di memori untuk pengujian (meniru sebagian API supabase-py)."""
from datetime import datetime, timezone


class FakeAPIError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


class Result:
    def __init__(self, data, count=None):
        self.data, self.count = data, count


UNIQUE = {
    "users": [("email",)],
    "categories": [("name",)],
    "enrollments": [("user_id", "course_id")],
    "lesson_progress": [("user_id", "lesson_id")],
}
FKS = {  # table: [(kolom, tabel_induk)]
    "courses": [("category_id", "categories"), ("instructor_id", "users")],
    "lessons": [("course_id", "courses")],
    "enrollments": [("user_id", "users"), ("course_id", "courses")],
    "lesson_progress": [("user_id", "users"), ("lesson_id", "lessons")],
}
CASCADE = {"courses": ["lessons", "enrollments"], "lessons": ["lesson_progress"], "users": ["enrollments", "lesson_progress"]}
DEFAULTS = {
    "users": {"role": "student"},
    "categories": {"description": ""},
    "courses": {"description": "", "level": "beginner", "is_published": False},
    "lessons": {"content": "", "video_url": None},
}
NOW = lambda: datetime.now(timezone.utc).isoformat()  # noqa: E731
TS = {"users": "created_at", "courses": "created_at", "lessons": "created_at",
      "enrollments": "enrolled_at", "lesson_progress": "completed_at"}


class FakeSupabase:
    def __init__(self):
        self.tables = {n: [] for n in ("users", "categories", "courses", "lessons", "enrollments", "lesson_progress")}
        self.seq = {n: 0 for n in self.tables}

    def table(self, name):
        return Query(self, name)

    def rows(self, name):
        if name == "course_stats":
            return [{"course_id": c["id"],
                     "lesson_count": sum(1 for l in self.tables["lessons"] if l["course_id"] == c["id"]),
                     "student_count": sum(1 for e in self.tables["enrollments"] if e["course_id"] == c["id"])}
                    for c in self.tables["courses"]]
        return self.tables[name]

    def delete_row(self, name, row):
        for child, cols in FKS.items():
            for col, parent in cols:
                if parent == name and any(r[col] == row["id"] for r in self.tables[child]):
                    if child in CASCADE.get(name, []):
                        continue
                    raise FakeAPIError("23503", "violates foreign key constraint")
        self.tables[name].remove(row)
        for child in CASCADE.get(name, []):
            for r in list(self.tables[child]):
                if any(r.get(col) == row["id"] and parent == name for col, parent in FKS[child]):
                    self.delete_row(child, r)


class Query:
    def __init__(self, db, name):
        self.db, self.name = db, name
        self.op, self.cols, self.count_mode, self.payload = "select", "*", None, None
        self.filters, self.orders, self.lim, self.rng = [], [], None, None

    def select(self, cols="*", count=None):
        self.op, self.cols, self.count_mode = "select", cols, count
        return self

    def insert(self, payload):
        self.op, self.payload = "insert", payload
        return self

    def update(self, payload):
        self.op, self.payload = "update", payload
        return self

    def delete(self):
        self.op = "delete"
        return self

    def eq(self, col, val):
        self.filters.append(lambda r: str(r.get(col)) == str(val) if not isinstance(val, bool) else r.get(col) is val)
        return self

    def in_(self, col, vals):
        self.filters.append(lambda r: r.get(col) in vals)
        return self

    def ilike(self, col, pattern):
        needle = pattern.strip("%").lower()
        self.filters.append(lambda r: needle in str(r.get(col, "")).lower())
        return self

    def order(self, col, desc=False):
        self.orders.append((col, desc))
        return self

    def limit(self, n):
        self.lim = n
        return self

    def range(self, a, b):
        self.rng = (a, b)
        return self

    def _match(self):
        rows = [r for r in self.db.rows(self.name) if all(f(r) for f in self.filters)]
        for col, desc in reversed(self.orders):
            rows.sort(key=lambda r: (r.get(col) is None, r.get(col)), reverse=desc)
        return rows

    def _project(self, r):
        if self.cols == "*":
            return dict(r)
        return {c.strip(): r.get(c.strip()) for c in self.cols.split(",")}

    def execute(self):
        db, name = self.db, self.name
        if self.op == "select":
            rows = self._match()
            total = len(rows)
            if self.rng:
                rows = rows[self.rng[0]: self.rng[1] + 1]
            if self.lim is not None:
                rows = rows[: self.lim]
            return Result([self._project(r) for r in rows], total if self.count_mode else None)
        if self.op == "insert":
            row = {**DEFAULTS.get(name, {}), **self.payload}
            for cols in UNIQUE.get(name, []):
                if any(all(r[c] == row[c] for c in cols) for r in db.tables[name]):
                    raise FakeAPIError("23505", "duplicate key")
            for col, parent in FKS.get(name, []):
                if not any(p["id"] == row[col] for p in db.tables[parent]):
                    raise FakeAPIError("23503", "violates foreign key constraint")
            db.seq[name] += 1
            row["id"] = db.seq[name]
            if name in TS:
                row.setdefault(TS[name], NOW())
            if name == "courses":
                row.setdefault("updated_at", NOW())
            db.tables[name].append(row)
            return Result([dict(row)])
        rows = self._match()
        if self.op == "update":
            for r in rows:
                r.update(self.payload)
            return Result([dict(r) for r in rows])
        for r in rows:
            db.delete_row(name, r)
        return Result([])
