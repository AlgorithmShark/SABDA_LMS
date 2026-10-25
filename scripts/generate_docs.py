"""Membuat docs/API.md, postman/*.json, dan memperbarui bagian endpoint di README.md.
Jalankan dari root proyek:  python scripts/generate_docs.py"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api_spec import BASE, ENDPOINTS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda o: json.dumps(o, indent=2, ensure_ascii=False)  # noqa: E731
ROLE_LABEL = {"student": "student", "instructor": "instructor", "admin": "admin"}


def endpoint_md(e, n):
    headers = []
    if e["body"] is not None:
        headers.append("Content-Type: application/json")
    if e["auth"]:
        headers.append("Authorization: Bearer <token>")
    access = "Publik" if not e["auth"] else ("Login (semua role)" if not e["roles"] else "Role: " + ", ".join(e["roles"]))
    lines = [f"#### {n}. {e['name']}", "",
             f"- **Method** : `{e['method']}`", f"- **URL** : `{BASE}{e['path']}`", f"- **Deskripsi** : {e['desc']}",
             f"- **Akses** : {access}", f"- **Headers** : {' | '.join(f'`{h}`' for h in headers) if headers else '-'}"]
    if e["body"] is not None:
        lines += ["- **Request Body** :", "", "```json", J(e["body"]), "```", ""]
    status, body = e["ok"]
    lines += [f"- **Response Sukses ({status})** :", ""]
    lines += ["```json", J(body), "```", ""] if body else ["  (tanpa body)", ""]
    for code, msg in e["errors"]:
        payload = msg if msg.startswith("{") else J({"error": msg}).replace("\n", "").replace("  ", "")
        lines.append(f"- **Response Error ({code})** : `{payload}`")
    return "\n".join(lines) + "\n"


def docs_md():
    out, group, n = [], None, 0
    for e in ENDPOINTS:
        n += 1
        if e["group"] != group:
            group = e["group"]
            out.append(f"### {group}\n")
        out.append(endpoint_md(e, n))
    return "\n".join(out)


def postman():
    folders = {}
    for e in ENDPOINTS:
        path, _, query = e["path"].partition("?")
        req = {"method": e["method"], "header": [], "url": {
            "raw": "{{base_url}}" + e["path"], "host": ["{{base_url}}"], "path": path.strip("/").split("/"),
            "query": [{"key": k, "value": v} for k, v in (p.split("=") for p in query.split("&"))] if query else []},
            "description": e["desc"]}
        if e["body"] is not None:
            req["header"].append({"key": "Content-Type", "value": "application/json"})
            req["body"] = {"mode": "raw", "raw": J(e["body"]), "options": {"raw": {"language": "json"}}}
        if not e["auth"]:
            req["auth"] = {"type": "noauth"}
        item = {"name": e["name"], "request": req}
        if e["path"] in ("/api/auth/login", "/api/auth/register"):
            item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": [
                "const r = pm.response.json();",
                "if (r.data && r.data.token) { pm.collectionVariables.set('token', r.data.token); }"]}}]
        folders.setdefault(e["group"], []).append(item)
    return {
        "info": {"name": "SABDA LMS API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                 "description": "Jalankan 'Login' lebih dulu; token tersimpan otomatis di variabel {{token}}. "
                                "Ganti base_url dengan URL Vercel Anda."},
        "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{token}}", "type": "string"}]},
        "variable": [{"key": "base_url", "value": BASE}, {"key": "token", "value": ""}],
        "item": [{"name": g, "item": items} for g, items in folders.items()],
    }


def main():
    md = docs_md()
    with open(os.path.join(ROOT, "docs", "API.md"), "w", encoding="utf-8") as f:
        f.write("# Dokumentasi Endpoint SABDA LMS API\n\nGanti `" + BASE + "` dengan URL deployment Vercel Anda.\n\n" + md)
    with open(os.path.join(ROOT, "postman", "SABDA-LMS.postman_collection.json"), "w", encoding="utf-8") as f:
        f.write(J(postman()))
    readme = os.path.join(ROOT, "README.md")
    if os.path.exists(readme):
        text = open(readme, encoding="utf-8").read()
        new = re.sub(r"(<!-- API-DOCS:START -->).*?(<!-- API-DOCS:END -->)",
                     lambda m: f"{m.group(1)}\n\n{md}\n{m.group(2)}", text, flags=re.S)
        open(readme, "w", encoding="utf-8").write(new)
    print(f"{len(ENDPOINTS)} endpoint didokumentasikan")


if __name__ == "__main__":
    main()
